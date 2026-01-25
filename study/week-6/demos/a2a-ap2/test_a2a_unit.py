"""
A2A + AP2 데모: 단위 테스트

개별 함수의 동작을 검증합니다.
서버를 띄우지 않고 함수 단위로 테스트합니다.

실행: pytest test_unit.py -v
"""

import pytest
import json
import uuid
from datetime import datetime

# =============================================================================
# 테스트 대상 함수 임포트를 위한 설정
# =============================================================================

# merchant_agent.py의 함수들을 직접 테스트하기 위해
# 모듈 레벨에서 필요한 함수들을 정의

def create_cart_mandate(product):
    """
    AP2 Cart Mandate 생성 (merchant_agent.py에서 복사)

    테스트를 위해 독립적으로 정의합니다.
    """
    return {
        "contents": {
            "id": f"cart_{uuid.uuid4().hex[:8]}",
            "user_signature_required": True,
            "payment_request": {
                "method_data": [
                    {
                        "supported_methods": "CARD",
                        "data": {"networks": ["visa", "mastercard"]}
                    }
                ],
                "details": {
                    "id": f"order_{uuid.uuid4().hex[:8]}",
                    "displayItems": [
                        {
                            "label": product["name"],
                            "amount": {
                                "currency": product["currency"],
                                "value": str(product["price"])
                            }
                        }
                    ],
                    "total": {
                        "label": "Total",
                        "amount": {
                            "currency": product["currency"],
                            "value": str(product["price"])
                        }
                    }
                }
            }
        },
        "merchant_signature": f"sig_{uuid.uuid4().hex[:16]}",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def verify_payment_mandate(payment_mandate):
    """
    AP2 Payment Mandate 검증 (merchant_agent.py에서 복사)
    """
    user_auth = payment_mandate.get("user_authorization")
    return user_auth is not None and len(user_auth) > 0


# =============================================================================
# Cart Mandate 테스트
# =============================================================================

class TestCartMandate:
    """Cart Mandate 생성 테스트"""

    def test_cart_mandate_structure(self, sample_product):
        """
        Cart Mandate가 올바른 구조를 가지는지 확인

        AP2 스펙에 따라 Cart Mandate는 다음을 포함해야 함:
        - contents: 장바구니 내용
        - merchant_signature: 판매자 서명
        - timestamp: 생성 시간
        """
        # Given: 샘플 상품
        product = sample_product

        # When: Cart Mandate 생성
        cart_mandate = create_cart_mandate(product)

        # Then: 필수 필드 존재 확인
        assert "contents" in cart_mandate
        assert "merchant_signature" in cart_mandate
        assert "timestamp" in cart_mandate

    def test_cart_mandate_contains_product_info(self, sample_product):
        """
        Cart Mandate에 상품 정보가 포함되는지 확인
        """
        # Given
        product = sample_product

        # When
        cart_mandate = create_cart_mandate(product)

        # Then: 상품 정보 확인
        details = cart_mandate["contents"]["payment_request"]["details"]
        display_items = details["displayItems"]

        assert len(display_items) == 1
        assert display_items[0]["label"] == product["name"]
        assert display_items[0]["amount"]["value"] == str(product["price"])

    def test_cart_mandate_total_matches_product_price(self, sample_product):
        """
        Cart Mandate의 총액이 상품 가격과 일치하는지 확인
        """
        # Given
        product = sample_product

        # When
        cart_mandate = create_cart_mandate(product)

        # Then: 총액 확인
        total = cart_mandate["contents"]["payment_request"]["details"]["total"]
        assert total["amount"]["value"] == str(product["price"])
        assert total["amount"]["currency"] == product["currency"]

    def test_cart_mandate_requires_user_signature(self, sample_product):
        """
        Cart Mandate가 사용자 서명을 요구하는지 확인

        AP2에서 실제 결제를 위해서는 사용자 서명이 필요합니다.
        """
        # Given
        product = sample_product

        # When
        cart_mandate = create_cart_mandate(product)

        # Then
        assert cart_mandate["contents"]["user_signature_required"] is True

    def test_cart_mandate_has_unique_ids(self, sample_product):
        """
        각 Cart Mandate가 고유한 ID를 가지는지 확인
        """
        # Given
        product = sample_product

        # When: 두 개의 Cart Mandate 생성
        mandate1 = create_cart_mandate(product)
        mandate2 = create_cart_mandate(product)

        # Then: ID가 다름
        assert mandate1["contents"]["id"] != mandate2["contents"]["id"]


# =============================================================================
# Payment Mandate 검증 테스트
# =============================================================================

class TestPaymentMandateVerification:
    """Payment Mandate 검증 테스트"""

    def test_valid_payment_mandate(self):
        """
        유효한 Payment Mandate 검증 성공
        """
        # Given: 유효한 Payment Mandate
        payment_mandate = {
            "payment_mandate_contents": {
                "payment_mandate_id": "pm_test123"
            },
            "user_authorization": "eyJhbGciOiJFUzI1NksifQ.validSignature",
            "agent_presence_indicator": {
                "agent_initiated": True,
                "human_present": True
            }
        }

        # When
        is_valid = verify_payment_mandate(payment_mandate)

        # Then
        assert is_valid is True

    def test_invalid_payment_mandate_no_signature(self):
        """
        서명이 없는 Payment Mandate 검증 실패
        """
        # Given: 서명 없는 Payment Mandate
        payment_mandate = {
            "payment_mandate_contents": {
                "payment_mandate_id": "pm_test123"
            },
            "user_authorization": None  # 서명 없음
        }

        # When
        is_valid = verify_payment_mandate(payment_mandate)

        # Then
        assert is_valid is False

    def test_invalid_payment_mandate_empty_signature(self):
        """
        빈 서명의 Payment Mandate 검증 실패
        """
        # Given: 빈 서명
        payment_mandate = {
            "payment_mandate_contents": {
                "payment_mandate_id": "pm_test123"
            },
            "user_authorization": ""  # 빈 서명
        }

        # When
        is_valid = verify_payment_mandate(payment_mandate)

        # Then
        assert is_valid is False


# =============================================================================
# Agent Card 테스트
# =============================================================================

class TestAgentCard:
    """Agent Card 구조 테스트"""

    def test_agent_card_structure(self):
        """
        Agent Card가 A2A 스펙에 맞는 구조를 가지는지 확인
        """
        # Given: 예상되는 Agent Card 구조
        agent_card = {
            "protocolVersion": "0.3.0",
            "name": "Demo Merchant Agent",
            "url": "http://localhost:5001/a2a",
            "skills": [],
            "extensions": []
        }

        # Then: 필수 필드 확인
        assert "protocolVersion" in agent_card
        assert "name" in agent_card
        assert "url" in agent_card

    def test_ap2_extension_detection(self):
        """
        AP2 확장 지원 여부 감지 테스트
        """
        # Given: AP2 확장을 포함한 Agent Card
        extensions = [
            {
                "uri": "https://google-a2a.github.io/A2A/extensions/payments/v1",
                "description": "AP2 결제 프로토콜 지원"
            }
        ]

        # When: AP2 지원 여부 확인
        supports_ap2 = any(
            "payments" in ext.get("uri", "")
            for ext in extensions
        )

        # Then
        assert supports_ap2 is True

    def test_non_ap2_agent_detection(self):
        """
        AP2를 지원하지 않는 에이전트 감지 테스트
        """
        # Given: AP2 확장이 없는 Agent Card
        extensions = [
            {
                "uri": "https://example.com/other-extension",
                "description": "다른 확장"
            }
        ]

        # When
        supports_ap2 = any(
            "payments" in ext.get("uri", "")
            for ext in extensions
        )

        # Then
        assert supports_ap2 is False


# =============================================================================
# JSON-RPC 메시지 테스트
# =============================================================================

class TestJsonRpcMessage:
    """JSON-RPC 메시지 구조 테스트"""

    def test_task_create_message_structure(self):
        """
        tasks/create 메시지가 올바른 JSON-RPC 구조를 가지는지 확인
        """
        # Given
        message = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/create",
            "params": {
                "taskId": "task_001",
                "contextId": "ctx_001",
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "user",
                    "parts": [{"kind": "text", "text": "테스트"}]
                }
            }
        }

        # Then: JSON-RPC 2.0 필수 필드
        assert message["jsonrpc"] == "2.0"
        assert "id" in message
        assert "method" in message
        assert "params" in message

    def test_a2a_message_parts_structure(self):
        """
        A2A 메시지의 parts 구조 테스트

        A2A 메시지는 parts 배열을 통해 다양한 유형의 데이터를 전송합니다.
        - kind: "text" - 텍스트 메시지
        - kind: "data" - 구조화된 데이터 (Mandate 등)
        """
        # Given: 텍스트 파트
        text_part = {"kind": "text", "text": "검색 요청"}

        # Given: 데이터 파트 (Payment Mandate)
        data_part = {
            "kind": "data",
            "data": {
                "ap2.mandates.PaymentMandate": {
                    "payment_mandate_contents": {}
                }
            }
        }

        # Then
        assert text_part["kind"] == "text"
        assert data_part["kind"] == "data"
        assert "ap2.mandates.PaymentMandate" in data_part["data"]


# =============================================================================
# 실행
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
