"""
UCP 데모: 통합 테스트

실제 서버를 띄우고 UCP의 전체 상거래 플로우를 테스트합니다.

실행: pytest test_integration.py -v
"""

import pytest
import json
import sys
import os

# merchant_server 모듈 임포트
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from merchant_server import app, CHECKOUT_SESSIONS, ORDERS


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def client():
    """
    Flask 테스트 클라이언트
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        # 각 테스트 전에 저장소 초기화
        CHECKOUT_SESSIONS.clear()
        ORDERS.clear()
        yield client


# =============================================================================
# Capability Profile 테스트
# =============================================================================

class TestCapabilityDiscovery:
    """
    UCP Capability 발견 테스트

    AI 에이전트는 /.well-known/ucp.json을 통해
    비즈니스가 지원하는 기능을 발견합니다.
    """

    def test_capability_profile_endpoint(self, client):
        """
        Capability Profile 엔드포인트가 200을 반환
        """
        # When
        response = client.get("/.well-known/ucp.json")

        # Then
        assert response.status_code == 200

    def test_capability_profile_contains_merchant_info(self, client):
        """
        Capability Profile에 상점 정보 포함
        """
        # When
        response = client.get("/.well-known/ucp.json")
        data = json.loads(response.data)

        # Then
        assert "merchant" in data
        assert "name" in data["merchant"]

    def test_capability_profile_lists_capabilities(self, client):
        """
        Capability Profile에 사용 가능한 기능 목록 포함
        """
        # When
        response = client.get("/.well-known/ucp.json")
        data = json.loads(response.data)

        # Then
        assert "capabilities" in data
        assert "discovery" in data["capabilities"]
        assert "checkout" in data["capabilities"]

    def test_discovery_capability_endpoints(self, client):
        """
        Discovery Capability의 엔드포인트 정보 확인
        """
        # When
        response = client.get("/.well-known/ucp.json")
        data = json.loads(response.data)

        # Then
        discovery = data["capabilities"]["discovery"]
        assert discovery["product_search"]["endpoint"] == "/ucp/discovery/search"
        assert discovery["product_search"]["method"] == "POST"


# =============================================================================
# Product Discovery 테스트
# =============================================================================

class TestProductDiscovery:
    """
    UCP Discovery Capability 테스트

    상품 검색 및 상세 조회 기능을 테스트합니다.
    """

    def test_search_products_returns_results(self, client):
        """
        상품 검색이 결과를 반환
        """
        # When
        response = client.post(
            "/ucp/discovery/search",
            data=json.dumps({"query": "rose", "page_size": 10}),
            content_type="application/json"
        )
        data = json.loads(response.data)

        # Then
        assert response.status_code == 200
        assert data["success"] is True
        assert "products" in data["data"]

    def test_search_with_empty_query_returns_all(self, client):
        """
        빈 쿼리로 검색하면 모든 상품 반환
        """
        # When
        response = client.post(
            "/ucp/discovery/search",
            data=json.dumps({"query": ""}),
            content_type="application/json"
        )
        data = json.loads(response.data)

        # Then
        assert data["success"] is True
        assert len(data["data"]["products"]) > 0

    def test_search_respects_page_size(self, client):
        """
        page_size 파라미터가 적용되는지 확인
        """
        # When
        response = client.post(
            "/ucp/discovery/search",
            data=json.dumps({"query": "", "page_size": 2}),
            content_type="application/json"
        )
        data = json.loads(response.data)

        # Then
        assert len(data["data"]["products"]) <= 2

    def test_get_product_details(self, client):
        """
        상품 상세 정보 조회
        """
        # When
        response = client.get("/ucp/discovery/product/flower-001")
        data = json.loads(response.data)

        # Then
        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["id"] == "flower-001"

    def test_get_nonexistent_product_returns_404(self, client):
        """
        존재하지 않는 상품 조회 시 404 반환
        """
        # When
        response = client.get("/ucp/discovery/product/nonexistent")

        # Then
        assert response.status_code == 404


# =============================================================================
# Checkout Session 테스트
# =============================================================================

class TestCheckoutSession:
    """
    UCP Checkout Session 테스트

    결제 세션 생성 및 관리 기능을 테스트합니다.
    """

    def test_create_checkout_session(self, client):
        """
        결제 세션 생성 성공
        """
        # When
        response = client.post(
            "/ucp/checkout/session",
            data=json.dumps({
                "cart": {
                    "items": [{"product_id": "flower-001", "quantity": 1}]
                },
                "shipping_option": "standard"
            }),
            content_type="application/json"
        )
        data = json.loads(response.data)

        # Then
        assert response.status_code == 200
        assert data["success"] is True
        assert "session_id" in data["data"]

    def test_checkout_session_calculates_total(self, client):
        """
        결제 세션이 총액을 정확히 계산
        """
        # When
        response = client.post(
            "/ucp/checkout/session",
            data=json.dumps({
                "cart": {
                    "items": [{"product_id": "flower-001", "quantity": 2}]
                },
                "shipping_option": "standard"
            }),
            content_type="application/json"
        )
        data = json.loads(response.data)
        session = data["data"]

        # Then: flower-001 가격 $45 x 2 + 배송비 $5 = $95
        assert session["subtotal"]["value"] == "90.00"
        assert session["shipping"]["cost"]["value"] == "5.00"
        assert session["total"]["value"] == "95.00"

    def test_checkout_session_with_express_shipping(self, client):
        """
        빠른 배송 옵션 선택 시 배송비 반영
        """
        # When
        response = client.post(
            "/ucp/checkout/session",
            data=json.dumps({
                "cart": {
                    "items": [{"product_id": "flower-001", "quantity": 1}]
                },
                "shipping_option": "express"
            }),
            content_type="application/json"
        )
        data = json.loads(response.data)
        session = data["data"]

        # Then: $45 + 빠른 배송 $15 = $60
        assert session["shipping"]["cost"]["value"] == "15.00"
        assert session["total"]["value"] == "60.00"

    def test_checkout_session_status_is_pending(self, client):
        """
        새 결제 세션의 상태가 pending
        """
        # When
        response = client.post(
            "/ucp/checkout/session",
            data=json.dumps({
                "cart": {"items": [{"product_id": "flower-001", "quantity": 1}]}
            }),
            content_type="application/json"
        )
        data = json.loads(response.data)

        # Then
        assert data["data"]["status"] == "pending"


# =============================================================================
# Order Submission 테스트
# =============================================================================

class TestOrderSubmission:
    """
    UCP 주문 제출 테스트

    결제 세션을 기반으로 주문을 생성합니다.
    """

    def test_submit_order_success(self, client):
        """
        주문 제출 성공
        """
        # Given: 먼저 결제 세션 생성
        session_response = client.post(
            "/ucp/checkout/session",
            data=json.dumps({
                "cart": {"items": [{"product_id": "flower-001", "quantity": 1}]}
            }),
            content_type="application/json"
        )
        session = json.loads(session_response.data)["data"]

        # When: 주문 제출
        order_response = client.post(
            "/ucp/checkout/submit",
            data=json.dumps({
                "session_id": session["session_id"],
                "payment": {"method": "CARD", "token": "tok_test_4242"},
                "shipping_address": {
                    "recipient": "홍길동",
                    "address_line": ["서울시 강남구"],
                    "city": "서울",
                    "postal_code": "06164",
                    "country": "KR"
                }
            }),
            content_type="application/json"
        )
        data = json.loads(order_response.data)

        # Then
        assert order_response.status_code == 200
        assert data["success"] is True
        assert "order" in data["data"]
        assert data["data"]["order"]["status"] == "confirmed"

    def test_submit_order_creates_transaction(self, client):
        """
        주문 제출 시 거래 ID 생성
        """
        # Given
        session_response = client.post(
            "/ucp/checkout/session",
            data=json.dumps({
                "cart": {"items": [{"product_id": "flower-001", "quantity": 1}]}
            }),
            content_type="application/json"
        )
        session = json.loads(session_response.data)["data"]

        # When
        order_response = client.post(
            "/ucp/checkout/submit",
            data=json.dumps({
                "session_id": session["session_id"],
                "payment": {"method": "CARD", "token": "tok_test"},
                "shipping_address": {"recipient": "Test"}
            }),
            content_type="application/json"
        )
        data = json.loads(order_response.data)

        # Then
        assert "transaction_id" in data["data"]["order"]["payment"]

    def test_submit_order_with_invalid_session_fails(self, client):
        """
        잘못된 세션 ID로 주문 시 실패
        """
        # When
        response = client.post(
            "/ucp/checkout/submit",
            data=json.dumps({
                "session_id": "invalid_session_id",
                "payment": {"method": "CARD"},
                "shipping_address": {}
            }),
            content_type="application/json"
        )

        # Then
        assert response.status_code == 404

    def test_submit_order_twice_fails(self, client):
        """
        같은 세션으로 두 번 주문 시 실패
        """
        # Given: 세션 생성 및 첫 번째 주문
        session_response = client.post(
            "/ucp/checkout/session",
            data=json.dumps({
                "cart": {"items": [{"product_id": "flower-001", "quantity": 1}]}
            }),
            content_type="application/json"
        )
        session = json.loads(session_response.data)["data"]

        # 첫 번째 주문
        client.post(
            "/ucp/checkout/submit",
            data=json.dumps({
                "session_id": session["session_id"],
                "payment": {"method": "CARD"},
                "shipping_address": {}
            }),
            content_type="application/json"
        )

        # When: 두 번째 주문 시도
        response = client.post(
            "/ucp/checkout/submit",
            data=json.dumps({
                "session_id": session["session_id"],
                "payment": {"method": "CARD"},
                "shipping_address": {}
            }),
            content_type="application/json"
        )

        # Then: 이미 처리된 세션이므로 실패
        assert response.status_code == 400


# =============================================================================
# Full Shopping Flow 테스트
# =============================================================================

class TestFullShoppingFlow:
    """
    전체 쇼핑 플로우 테스트

    1. Capability 발견
    2. 상품 검색
    3. 결제 세션 생성
    4. 주문 제출
    """

    def test_complete_shopping_flow(self, client):
        """
        전체 쇼핑 플로우가 성공적으로 완료되는지 확인
        """
        # Step 1: Capability 발견
        cap_response = client.get("/.well-known/ucp.json")
        assert cap_response.status_code == 200
        capabilities = json.loads(cap_response.data)
        assert capabilities["merchant"]["name"] == "Demo Flower Shop"

        # Step 2: 상품 검색
        search_response = client.post(
            "/ucp/discovery/search",
            data=json.dumps({"query": "rose"}),
            content_type="application/json"
        )
        search_data = json.loads(search_response.data)
        assert search_data["success"] is True
        products = search_data["data"]["products"]
        assert len(products) > 0

        selected_product = products[0]
        print(f"\n선택된 상품: {selected_product['title']}")

        # Step 3: 결제 세션 생성
        session_response = client.post(
            "/ucp/checkout/session",
            data=json.dumps({
                "cart": {
                    "items": [{"product_id": selected_product["id"], "quantity": 1}]
                },
                "shipping_option": "standard"
            }),
            content_type="application/json"
        )
        session_data = json.loads(session_response.data)
        assert session_data["success"] is True
        session = session_data["data"]
        print(f"결제 세션 생성: {session['session_id']}")
        print(f"총액: {session['total']['value']} {session['total']['currency']}")

        # Step 4: 주문 제출
        order_response = client.post(
            "/ucp/checkout/submit",
            data=json.dumps({
                "session_id": session["session_id"],
                "payment": {"method": "CARD", "token": "tok_visa_4242"},
                "shipping_address": {
                    "recipient": "홍길동",
                    "address_line": ["서울시 강남구 테헤란로 123"],
                    "city": "서울",
                    "postal_code": "06164",
                    "country": "KR"
                }
            }),
            content_type="application/json"
        )
        order_data = json.loads(order_response.data)
        assert order_data["success"] is True
        order = order_data["data"]["order"]

        # 최종 확인
        assert order["status"] == "confirmed"
        assert order["payment"]["status"] == "paid"
        print(f"\n✓ 주문 완료! Order ID: {order['order_id']}")
        print(f"✓ 예상 배송일: {order['estimated_delivery']}")


# =============================================================================
# 실행
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
