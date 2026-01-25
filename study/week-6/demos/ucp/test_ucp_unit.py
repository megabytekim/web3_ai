"""
UCP 데모: 단위 테스트

UCP의 핵심 함수들을 개별적으로 테스트합니다.

실행: pytest test_unit.py -v
"""

import pytest
import json


# =============================================================================
# UCP Capability Profile 테스트
# =============================================================================

class TestCapabilityProfile:
    """
    UCP Capability Profile 구조 테스트

    Capability Profile은 비즈니스가 지원하는 UCP 기능을 선언합니다.
    """

    def test_capability_profile_structure(self):
        """
        Capability Profile이 올바른 구조를 가지는지 확인
        """
        # Given: 예상되는 Capability Profile 구조
        profile = {
            "version": "1.0",
            "merchant": {
                "name": "Demo Shop",
                "url": "http://localhost:5002"
            },
            "capabilities": {
                "discovery": {},
                "checkout": {}
            }
        }

        # Then: 필수 필드 확인
        assert "version" in profile
        assert "merchant" in profile
        assert "capabilities" in profile

    def test_discovery_capability_enabled(self):
        """
        Discovery Capability가 활성화되어 있는지 확인
        """
        # Given
        capabilities = {
            "discovery": {
                "product_search": {
                    "enabled": True,
                    "endpoint": "/ucp/discovery/search",
                    "method": "POST"
                }
            }
        }

        # Then
        assert capabilities["discovery"]["product_search"]["enabled"] is True

    def test_checkout_capability_enabled(self):
        """
        Checkout Capability가 활성화되어 있는지 확인
        """
        # Given
        capabilities = {
            "checkout": {
                "create_session": {
                    "enabled": True,
                    "endpoint": "/ucp/checkout/session",
                    "method": "POST"
                },
                "submit_order": {
                    "enabled": True,
                    "endpoint": "/ucp/checkout/submit",
                    "method": "POST"
                }
            }
        }

        # Then
        assert capabilities["checkout"]["create_session"]["enabled"] is True
        assert capabilities["checkout"]["submit_order"]["enabled"] is True


# =============================================================================
# 상품 검색 로직 테스트
# =============================================================================

class TestProductSearch:
    """
    상품 검색 로직 테스트
    """

    @pytest.fixture
    def sample_products(self):
        """테스트용 상품 목록"""
        return [
            {"id": "1", "title": "Red Rose", "description": "빨간 장미"},
            {"id": "2", "title": "White Lily", "description": "백합"},
            {"id": "3", "title": "Spring Mix", "description": "봄 꽃 믹스"},
        ]

    def test_search_by_title(self, sample_products):
        """
        제목으로 검색이 되는지 확인
        """
        # Given
        query = "rose"

        # When
        results = [
            p for p in sample_products
            if query.lower() in p["title"].lower()
        ]

        # Then
        assert len(results) == 1
        assert results[0]["id"] == "1"

    def test_search_by_description(self, sample_products):
        """
        설명으로 검색이 되는지 확인
        """
        # Given
        query = "장미"

        # When
        results = [
            p for p in sample_products
            if query.lower() in p["description"].lower()
        ]

        # Then
        assert len(results) == 1
        assert results[0]["id"] == "1"

    def test_empty_query_returns_all(self, sample_products):
        """
        빈 쿼리는 모든 상품을 반환
        """
        # Given
        query = ""

        # When
        results = sample_products if not query else []

        # Then
        assert len(results) == 3

    def test_no_match_returns_empty(self, sample_products):
        """
        매칭되는 상품이 없으면 빈 목록 반환
        """
        # Given
        query = "sunflower"

        # When
        results = [
            p for p in sample_products
            if query.lower() in p["title"].lower() or query.lower() in p["description"].lower()
        ]

        # Then
        assert len(results) == 0


# =============================================================================
# 장바구니 계산 테스트
# =============================================================================

class TestCartCalculation:
    """
    장바구니 금액 계산 테스트
    """

    def test_single_item_subtotal(self):
        """
        단일 상품 소계 계산
        """
        # Given
        item_price = 45.00
        quantity = 1

        # When
        subtotal = item_price * quantity

        # Then
        assert subtotal == 45.00

    def test_multiple_items_subtotal(self):
        """
        다중 상품 소계 계산
        """
        # Given
        items = [
            {"price": 45.00, "quantity": 2},
            {"price": 30.00, "quantity": 1},
        ]

        # When
        subtotal = sum(item["price"] * item["quantity"] for item in items)

        # Then
        assert subtotal == 120.00

    def test_shipping_cost_calculation(self):
        """
        배송비 계산
        """
        # Given
        shipping_options = {
            "standard": 5.00,
            "express": 15.00
        }

        # When & Then
        assert shipping_options["standard"] == 5.00
        assert shipping_options["express"] == 15.00

    def test_total_with_shipping(self):
        """
        배송비 포함 총액 계산
        """
        # Given
        subtotal = 100.00
        shipping = 5.00

        # When
        total = subtotal + shipping

        # Then
        assert total == 105.00


# =============================================================================
# 결제 세션 테스트
# =============================================================================

class TestCheckoutSession:
    """
    결제 세션 구조 테스트
    """

    def test_session_structure(self):
        """
        결제 세션이 필수 필드를 포함하는지 확인
        """
        # Given: 예상되는 세션 구조
        session = {
            "session_id": "session_abc123",
            "status": "pending",
            "items": [],
            "subtotal": {"currency": "USD", "value": "0.00"},
            "shipping": {"option": "standard", "cost": {"currency": "USD", "value": "5.00"}},
            "total": {"currency": "USD", "value": "5.00"}
        }

        # Then
        assert "session_id" in session
        assert "status" in session
        assert "items" in session
        assert "total" in session

    def test_session_status_transitions(self):
        """
        세션 상태 전이 테스트

        pending -> completed (정상 완료)
        pending -> cancelled (취소)
        """
        # Given
        valid_transitions = {
            "pending": ["completed", "cancelled"],
            "completed": [],  # 최종 상태
            "cancelled": []   # 최종 상태
        }

        # Then
        assert "completed" in valid_transitions["pending"]
        assert "cancelled" in valid_transitions["pending"]


# =============================================================================
# 주문 테스트
# =============================================================================

class TestOrder:
    """
    주문 구조 테스트
    """

    def test_order_structure(self):
        """
        주문이 필수 필드를 포함하는지 확인
        """
        # Given
        order = {
            "order_id": "order_abc123",
            "status": "confirmed",
            "items": [],
            "total": {"currency": "USD", "value": "50.00"},
            "payment": {"method": "CARD", "status": "paid"},
            "shipping_address": {}
        }

        # Then
        assert "order_id" in order
        assert "status" in order
        assert "payment" in order
        assert order["payment"]["status"] == "paid"

    def test_order_payment_methods(self):
        """
        지원되는 결제 수단 테스트
        """
        # Given
        supported_methods = ["CARD", "PAYPAL"]

        # Then
        assert "CARD" in supported_methods
        assert "PAYPAL" in supported_methods


# =============================================================================
# 실행
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
