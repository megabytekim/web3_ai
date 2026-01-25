"""
A2A + AP2 데모: 통합 테스트

실제 서버를 띄우고 전체 플로우를 테스트합니다.
Flask 테스트 클라이언트를 사용하여 HTTP 요청을 시뮬레이션합니다.

실행: pytest test_integration.py -v
"""

import pytest
import json
import uuid
import sys
import os

# merchant_agent 모듈 임포트
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from merchant_agent import app, TASKS, PRODUCTS


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def client():
    """
    Flask 테스트 클라이언트

    실제 HTTP 서버를 띄우지 않고 요청을 테스트합니다.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        # 각 테스트 전에 TASKS 초기화
        TASKS.clear()
        yield client


@pytest.fixture
def sample_search_message():
    """검색 요청 메시지"""
    return {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tasks/create",
        "params": {
            "taskId": f"task_{uuid.uuid4().hex[:8]}",
            "contextId": f"ctx_{uuid.uuid4().hex[:8]}",
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [
                    {"kind": "text", "text": "빨간 운동화 찾아줘"}
                ]
            }
        }
    }


# =============================================================================
# Agent Card 테스트 (에이전트 발견)
# =============================================================================

class TestAgentDiscovery:
    """
    Step 1: 에이전트 발견 테스트

    A2A 프로토콜에서 클라이언트는 먼저 /.well-known/agent-card.json을
    통해 에이전트를 발견합니다.
    """

    def test_agent_card_endpoint_returns_200(self, client):
        """
        Agent Card 엔드포인트가 200을 반환하는지 확인
        """
        # When
        response = client.get("/.well-known/agent-card.json")

        # Then
        assert response.status_code == 200

    def test_agent_card_contains_required_fields(self, client):
        """
        Agent Card가 A2A 스펙의 필수 필드를 포함하는지 확인

        필수 필드:
        - protocolVersion: A2A 프로토콜 버전
        - name: 에이전트 이름
        - url: A2A 엔드포인트 URL
        """
        # When
        response = client.get("/.well-known/agent-card.json")
        data = json.loads(response.data)

        # Then
        assert "protocolVersion" in data
        assert "name" in data
        assert "url" in data

    def test_agent_card_declares_ap2_support(self, client):
        """
        Agent Card가 AP2 확장 지원을 선언하는지 확인

        AP2를 지원하는 에이전트는 extensions에 payments URI를 포함합니다.
        """
        # When
        response = client.get("/.well-known/agent-card.json")
        data = json.loads(response.data)

        # Then: AP2 확장 확인
        extensions = data.get("extensions", [])
        ap2_extension = next(
            (ext for ext in extensions if "payments" in ext.get("uri", "")),
            None
        )
        assert ap2_extension is not None

    def test_agent_card_lists_skills(self, client):
        """
        Agent Card가 제공하는 스킬 목록을 포함하는지 확인
        """
        # When
        response = client.get("/.well-known/agent-card.json")
        data = json.loads(response.data)

        # Then
        assert "skills" in data
        assert len(data["skills"]) > 0

        # 상품 검색 스킬 확인
        search_skill = next(
            (s for s in data["skills"] if s["id"] == "product-search"),
            None
        )
        assert search_skill is not None


# =============================================================================
# Task Creation 테스트 (검색 요청)
# =============================================================================

class TestTaskCreation:
    """
    Step 2: 태스크 생성 테스트

    클라이언트가 tasks/create 메서드로 검색 요청을 보내면
    서버는 Cart Mandate를 포함한 태스크를 반환합니다.
    """

    def test_task_create_returns_task(self, client, sample_search_message):
        """
        tasks/create가 태스크를 반환하는지 확인
        """
        # When
        response = client.post(
            "/a2a",
            data=json.dumps(sample_search_message),
            content_type="application/json"
        )
        data = json.loads(response.data)

        # Then
        assert response.status_code == 200
        assert "result" in data
        assert "id" in data["result"]

    def test_task_create_returns_cart_mandate(self, client, sample_search_message):
        """
        생성된 태스크에 Cart Mandate가 포함되는지 확인

        Cart Mandate는 AP2의 핵심 개념으로,
        판매자가 구매자에게 장바구니 확인을 요청하는 구조입니다.
        """
        # When
        response = client.post(
            "/a2a",
            data=json.dumps(sample_search_message),
            content_type="application/json"
        )
        data = json.loads(response.data)
        task = data["result"]

        # Then: artifacts에서 Cart Mandate 확인
        assert "artifacts" in task
        assert len(task["artifacts"]) > 0

        # Cart Mandate 추출
        cart_mandate = None
        for artifact in task["artifacts"]:
            for part in artifact.get("parts", []):
                if part.get("kind") == "data":
                    cart_mandate = part.get("data", {}).get("ap2.mandates.CartMandate")
                    if cart_mandate:
                        break

        assert cart_mandate is not None

    def test_task_status_is_input_required(self, client, sample_search_message):
        """
        생성된 태스크의 상태가 'input-required'인지 확인

        Cart Mandate를 받은 후 사용자의 결제 승인이 필요하므로
        상태는 'input-required'여야 합니다.
        """
        # When
        response = client.post(
            "/a2a",
            data=json.dumps(sample_search_message),
            content_type="application/json"
        )
        data = json.loads(response.data)
        task = data["result"]

        # Then
        assert task["status"]["state"] == "input-required"

    def test_task_is_stored_in_memory(self, client, sample_search_message):
        """
        생성된 태스크가 메모리에 저장되는지 확인
        """
        # Given
        task_id = sample_search_message["params"]["taskId"]

        # When
        client.post(
            "/a2a",
            data=json.dumps(sample_search_message),
            content_type="application/json"
        )

        # Then
        assert task_id in TASKS


# =============================================================================
# Payment Mandate 처리 테스트 (결제 실행)
# =============================================================================

class TestPaymentExecution:
    """
    Step 3-5: 결제 실행 테스트

    클라이언트가 Payment Mandate를 보내면
    서버는 결제를 검증하고 태스크를 완료합니다.
    """

    def test_payment_mandate_completes_task(self, client, sample_search_message):
        """
        유효한 Payment Mandate가 태스크를 완료하는지 확인
        """
        # Given: 먼저 태스크 생성
        response = client.post(
            "/a2a",
            data=json.dumps(sample_search_message),
            content_type="application/json"
        )
        task = json.loads(response.data)["result"]
        task_id = task["id"]
        context_id = task["contextId"]

        # When: Payment Mandate 전송
        payment_message = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "message/send",
            "params": {
                "taskId": task_id,
                "contextId": context_id,
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "user",
                    "parts": [
                        {
                            "kind": "data",
                            "data": {
                                "ap2.mandates.PaymentMandate": {
                                    "payment_mandate_contents": {
                                        "payment_mandate_id": f"pm_{uuid.uuid4().hex[:12]}",
                                        "payment_details_id": "order_001"
                                    },
                                    "user_authorization": "eyJhbGciOiJFUzI1NksifQ.validSignature",
                                    "agent_presence_indicator": {
                                        "agent_initiated": True,
                                        "human_present": True
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }

        response = client.post(
            "/a2a",
            data=json.dumps(payment_message),
            content_type="application/json"
        )
        result = json.loads(response.data)["result"]

        # Then: 태스크가 완료됨
        assert result["status"]["state"] == "completed"
        assert "transactionId" in result["status"]

    def test_invalid_payment_mandate_fails(self, client, sample_search_message):
        """
        유효하지 않은 Payment Mandate가 실패하는지 확인
        """
        # Given: 먼저 태스크 생성
        response = client.post(
            "/a2a",
            data=json.dumps(sample_search_message),
            content_type="application/json"
        )
        task = json.loads(response.data)["result"]
        task_id = task["id"]
        context_id = task["contextId"]

        # When: 서명 없는 Payment Mandate 전송
        payment_message = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "message/send",
            "params": {
                "taskId": task_id,
                "contextId": context_id,
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "user",
                    "parts": [
                        {
                            "kind": "data",
                            "data": {
                                "ap2.mandates.PaymentMandate": {
                                    "payment_mandate_contents": {},
                                    "user_authorization": "",  # 빈 서명
                                    "agent_presence_indicator": {}
                                }
                            }
                        }
                    ]
                }
            }
        }

        response = client.post(
            "/a2a",
            data=json.dumps(payment_message),
            content_type="application/json"
        )
        result = json.loads(response.data)["result"]

        # Then: 태스크가 실패함
        assert result["status"]["state"] == "failed"


# =============================================================================
# Task Get 테스트
# =============================================================================

class TestTaskGet:
    """
    tasks/get 메서드 테스트

    클라이언트는 언제든지 태스크 상태를 조회할 수 있습니다.
    """

    def test_get_existing_task(self, client, sample_search_message):
        """
        존재하는 태스크 조회 성공
        """
        # Given: 태스크 생성
        response = client.post(
            "/a2a",
            data=json.dumps(sample_search_message),
            content_type="application/json"
        )
        task = json.loads(response.data)["result"]
        task_id = task["id"]

        # When: 태스크 조회
        get_message = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/get",
            "params": {"taskId": task_id}
        }

        response = client.post(
            "/a2a",
            data=json.dumps(get_message),
            content_type="application/json"
        )
        result = json.loads(response.data)

        # Then
        assert "result" in result
        assert result["result"]["id"] == task_id

    def test_get_nonexistent_task_returns_error(self, client):
        """
        존재하지 않는 태스크 조회 시 에러 반환
        """
        # When
        get_message = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/get",
            "params": {"taskId": "nonexistent_task"}
        }

        response = client.post(
            "/a2a",
            data=json.dumps(get_message),
            content_type="application/json"
        )
        result = json.loads(response.data)

        # Then
        assert "error" in result


# =============================================================================
# Error Handling 테스트
# =============================================================================

class TestErrorHandling:
    """
    에러 처리 테스트

    잘못된 요청에 대해 적절한 에러를 반환하는지 확인합니다.
    """

    def test_unknown_method_returns_error(self, client):
        """
        알 수 없는 메서드 호출 시 에러 반환
        """
        # When
        message = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "unknown/method",
            "params": {}
        }

        response = client.post(
            "/a2a",
            data=json.dumps(message),
            content_type="application/json"
        )
        result = json.loads(response.data)

        # Then
        assert "error" in result
        assert result["error"]["code"] == -32601  # Method not found


# =============================================================================
# Full Flow 테스트
# =============================================================================

class TestFullPurchaseFlow:
    """
    전체 구매 플로우 테스트

    1. 에이전트 발견
    2. 검색 태스크 생성
    3. Cart Mandate 수신
    4. Payment Mandate 전송
    5. 결제 완료
    """

    def test_complete_purchase_flow(self, client):
        """
        전체 구매 플로우가 성공적으로 완료되는지 확인
        """
        # Step 1: 에이전트 발견
        response = client.get("/.well-known/agent-card.json")
        assert response.status_code == 200
        agent_card = json.loads(response.data)
        assert agent_card["name"] == "Demo Merchant Agent"

        # Step 2: 검색 태스크 생성
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        context_id = f"ctx_{uuid.uuid4().hex[:8]}"

        create_message = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/create",
            "params": {
                "taskId": task_id,
                "contextId": context_id,
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "user",
                    "parts": [{"kind": "text", "text": "빨간 운동화"}]
                }
            }
        }

        response = client.post(
            "/a2a",
            data=json.dumps(create_message),
            content_type="application/json"
        )
        task = json.loads(response.data)["result"]
        assert task["status"]["state"] == "input-required"

        # Step 3: Cart Mandate 확인
        cart_mandate = None
        for artifact in task["artifacts"]:
            for part in artifact["parts"]:
                if part.get("kind") == "data":
                    cart_mandate = part["data"].get("ap2.mandates.CartMandate")
        assert cart_mandate is not None

        # Step 4 & 5: Payment Mandate 전송 및 완료
        payment_message = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "message/send",
            "params": {
                "taskId": task_id,
                "contextId": context_id,
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "user",
                    "parts": [
                        {
                            "kind": "data",
                            "data": {
                                "ap2.mandates.PaymentMandate": {
                                    "payment_mandate_contents": {
                                        "payment_mandate_id": f"pm_{uuid.uuid4().hex[:12]}"
                                    },
                                    "user_authorization": "validSignature",
                                    "agent_presence_indicator": {
                                        "agent_initiated": True,
                                        "human_present": True
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }

        response = client.post(
            "/a2a",
            data=json.dumps(payment_message),
            content_type="application/json"
        )
        result = json.loads(response.data)["result"]

        # 최종 확인
        assert result["status"]["state"] == "completed"
        assert "transactionId" in result["status"]
        print(f"\n✓ 전체 플로우 성공! Transaction ID: {result['status']['transactionId']}")


# =============================================================================
# 실행
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
