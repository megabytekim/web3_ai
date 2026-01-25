"""
UCP (Universal Commerce Protocol) 데모: 클라이언트

이 클라이언트는 UCP를 통해 상점과 통신하여
상품 검색부터 주문 완료까지의 전체 플로우를 시연합니다.

공식 참고: https://github.com/Universal-Commerce-Protocol/samples
"""

import httpx
import json

MERCHANT_URL = "http://localhost:5002"


def main():
    print("=" * 50)
    print("UCP 데모: 쇼핑 클라이언트")
    print("=" * 50)

    client = UCPClient()
    client.run_shopping_flow()


class UCPClient:
    """UCP 클라이언트 - AI 에이전트 시뮬레이션"""

    def __init__(self):
        self.http = httpx.Client(timeout=30.0)

    def run_shopping_flow(self):
        """전체 쇼핑 플로우 실행"""

        # =========================================================
        # Step 1: Capability 발견
        # =========================================================
        print("\n[Step 1] UCP Capability 발견")
        capabilities = self.discover_capabilities()
        if not capabilities:
            print("  ❌ Capability Profile을 찾을 수 없습니다")
            return

        merchant = capabilities.get("merchant", {})
        print(f"  ✓ 상점: {merchant.get('name')}")

        caps = capabilities.get("capabilities", {})
        print(f"  ✓ Discovery 지원: {caps.get('discovery', {}).get('product_search', {}).get('enabled', False)}")
        print(f"  ✓ Checkout 지원: {caps.get('checkout', {}).get('create_session', {}).get('enabled', False)}")

        # =========================================================
        # Step 2: 상품 검색
        # =========================================================
        print("\n[Step 2] 상품 검색")
        search_result = self.search_products("rose")

        if not search_result or not search_result.get("success"):
            print("  ❌ 검색 실패")
            return

        products = search_result["data"]["products"]
        print(f"  ✓ 검색 결과: {len(products)}개")

        for p in products:
            print(f"    - {p['title']}: ${p['price']['value']}")

        if not products:
            print("  ❌ 상품이 없습니다")
            return

        selected_product = products[0]
        print(f"\n  선택된 상품: {selected_product['title']}")

        # =========================================================
        # Step 3: 결제 세션 생성
        # =========================================================
        print("\n[Step 3] 결제 세션 생성")
        session = self.create_checkout_session(selected_product["id"])

        if not session or not session.get("success"):
            print("  ❌ 세션 생성 실패")
            return

        session_data = session["data"]
        print(f"  ✓ Session ID: {session_data['session_id']}")
        print(f"  ✓ 상품 금액: ${session_data['subtotal']['value']}")
        print(f"  ✓ 배송비: ${session_data['shipping']['cost']['value']}")
        print(f"  ✓ 총액: ${session_data['total']['value']}")

        # =========================================================
        # Step 4: 주문 제출
        # =========================================================
        print("\n[Step 4] 주문 제출")

        # 시뮬레이션: 사용자 정보
        shipping_address = {
            "recipient": "홍길동",
            "address_line": ["서울시 강남구 테헤란로 123", "10층"],
            "city": "서울",
            "postal_code": "06164",
            "country": "KR"
        }

        payment_info = {
            "method": "CARD",
            "token": "tok_visa_demo_4242"
        }

        order_result = self.submit_order(
            session_data["session_id"],
            payment_info,
            shipping_address
        )

        if not order_result or not order_result.get("success"):
            print("  ❌ 주문 실패")
            return

        order = order_result["data"]["order"]
        print(f"  ✓ 주문 완료!")
        print(f"  ✓ Order ID: {order['order_id']}")
        print(f"  ✓ 상태: {order['status']}")
        print(f"  ✓ 결제: {order['payment']['status']}")
        print(f"  ✓ 예상 배송일: {order['estimated_delivery']}")

        print("\n" + "=" * 50)
        print("데모 종료")
        print("=" * 50)

    # =================================================================
    # UCP API 호출 메서드
    # =================================================================

    def discover_capabilities(self) -> dict:
        """
        UCP: Capability 발견

        /.well-known/ucp.json에서 상점의 UCP 기능을 조회합니다.
        """
        try:
            response = self.http.get(f"{MERCHANT_URL}/.well-known/ucp.json")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"  오류: {e}")
        return None

    def search_products(self, query: str) -> dict:
        """
        UCP Discovery: 상품 검색
        """
        try:
            response = self.http.post(
                f"{MERCHANT_URL}/ucp/discovery/search",
                json={
                    "query": query,
                    "page_size": 10
                }
            )
            return response.json()
        except Exception as e:
            print(f"  오류: {e}")
        return None

    def create_checkout_session(self, product_id: str) -> dict:
        """
        UCP Checkout: 결제 세션 생성
        """
        try:
            response = self.http.post(
                f"{MERCHANT_URL}/ucp/checkout/session",
                json={
                    "cart": {
                        "items": [
                            {"product_id": product_id, "quantity": 1}
                        ]
                    },
                    "shipping_option": "standard"
                }
            )
            return response.json()
        except Exception as e:
            print(f"  오류: {e}")
        return None

    def submit_order(self, session_id: str, payment: dict, shipping_address: dict) -> dict:
        """
        UCP Checkout: 주문 제출
        """
        try:
            response = self.http.post(
                f"{MERCHANT_URL}/ucp/checkout/submit",
                json={
                    "session_id": session_id,
                    "payment": payment,
                    "shipping_address": shipping_address
                }
            )
            return response.json()
        except Exception as e:
            print(f"  오류: {e}")
        return None


if __name__ == "__main__":
    main()
