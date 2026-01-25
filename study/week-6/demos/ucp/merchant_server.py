"""
UCP (Universal Commerce Protocol) 데모: 상점 서버

이 서버는 UCP의 핵심 Capabilities를 시뮬레이션합니다:
- Discovery: 상품 검색/조회
- Checkout: 결제 세션 및 주문 처리

공식 참고: https://github.com/Universal-Commerce-Protocol/samples
"""

from flask import Flask, jsonify, request
from datetime import datetime
import uuid
import json
import os

app = Flask(__name__)

# =============================================================================
# 데이터 로드
# =============================================================================

# 현재 파일 기준 상대 경로로 샘플 데이터 로드
_current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_current_dir, "sample_products.json"), "r") as f:
    PRODUCTS = json.load(f)["products"]

CHECKOUT_SESSIONS = {}  # 결제 세션 저장소
ORDERS = {}  # 주문 저장소


# =============================================================================
# UCP: Capability Profile (/.well-known/ucp.json)
# =============================================================================

@app.route("/.well-known/ucp.json", methods=["GET"])
def capability_profile():
    """
    UCP Capability Profile

    비즈니스가 지원하는 UCP Capabilities를 선언합니다.
    AI 에이전트는 이를 통해 어떤 기능을 사용할 수 있는지 발견합니다.
    """
    return jsonify({
        "version": "1.0",
        "merchant": {
            "name": "Demo Flower Shop",
            "description": "UCP 데모용 꽃집",
            "url": "http://localhost:5002"
        },

        # 지원하는 Capabilities 목록
        "capabilities": {
            # Discovery Capability
            "discovery": {
                "product_search": {
                    "enabled": True,
                    "endpoint": "/ucp/discovery/search",
                    "method": "POST"
                },
                "product_details": {
                    "enabled": True,
                    "endpoint": "/ucp/discovery/product/{product_id}",
                    "method": "GET"
                }
            },

            # Checkout Capability
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
            },

            # 지원하는 결제 수단
            "payment_methods": ["CARD", "PAYPAL"],

            # 지원하는 배송 옵션
            "shipping_options": [
                {"id": "standard", "label": "표준 배송", "price": "5.00", "currency": "USD"},
                {"id": "express", "label": "빠른 배송", "price": "15.00", "currency": "USD"}
            ]
        },

        # Transport 옵션 (REST, MCP, A2A)
        "transports": {
            "rest": {
                "base_url": "http://localhost:5002"
            }
            # MCP, A2A도 추가 가능
        }
    })


# =============================================================================
# UCP: Discovery Capability
# =============================================================================

@app.route("/ucp/discovery/search", methods=["POST"])
def product_search():
    """
    UCP Discovery: 상품 검색

    요청:
    {
        "query": "장미",
        "filters": {"category": "flowers"},
        "page_size": 10
    }
    """
    data = request.json or {}
    query = data.get("query", "").lower()
    page_size = data.get("page_size", 10)

    print(f"\n[UCP] 상품 검색: '{query}'")

    # 간단한 검색 로직
    results = []
    for product in PRODUCTS:
        if query in product["title"].lower() or query in product["description"].lower():
            results.append(product)

    # 쿼리가 비어있으면 전체 반환
    if not query:
        results = PRODUCTS

    print(f"[UCP] 검색 결과: {len(results)}개")

    return jsonify({
        "success": True,
        "data": {
            "products": results[:page_size],
            "total_results": len(results),
            "page": 1,
            "page_size": page_size
        }
    })


@app.route("/ucp/discovery/product/<product_id>", methods=["GET"])
def product_details(product_id):
    """
    UCP Discovery: 상품 상세 조회
    """
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)

    if not product:
        return jsonify({"success": False, "error": "Product not found"}), 404

    return jsonify({
        "success": True,
        "data": product
    })


# =============================================================================
# UCP: Checkout Capability
# =============================================================================

@app.route("/ucp/checkout/session", methods=["POST"])
def create_checkout_session():
    """
    UCP Checkout: 결제 세션 생성

    요청:
    {
        "cart": {
            "items": [
                {"product_id": "flower-001", "quantity": 1}
            ]
        },
        "shipping_option": "standard"
    }
    """
    data = request.json or {}
    cart = data.get("cart", {})
    shipping_option_id = data.get("shipping_option", "standard")

    print(f"\n[UCP] 결제 세션 생성")

    # 장바구니 아이템 처리
    items = []
    subtotal = 0.0

    for cart_item in cart.get("items", []):
        product = next((p for p in PRODUCTS if p["id"] == cart_item["product_id"]), None)
        if product:
            quantity = cart_item.get("quantity", 1)
            item_total = float(product["price"]["value"]) * quantity
            subtotal += item_total

            items.append({
                "product_id": product["id"],
                "title": product["title"],
                "quantity": quantity,
                "unit_price": product["price"],
                "total_price": {
                    "currency": "USD",
                    "value": f"{item_total:.2f}"
                }
            })

    # 배송비 계산
    shipping_options = {
        "standard": 5.00,
        "express": 15.00
    }
    shipping_cost = shipping_options.get(shipping_option_id, 5.00)

    # 총액 계산
    total = subtotal + shipping_cost

    # 세션 생성
    session_id = f"session_{uuid.uuid4().hex[:12]}"
    session = {
        "session_id": session_id,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "expires_at": "2026-01-26T00:00:00Z",  # 24시간 후

        "items": items,
        "subtotal": {"currency": "USD", "value": f"{subtotal:.2f}"},
        "shipping": {
            "option": shipping_option_id,
            "cost": {"currency": "USD", "value": f"{shipping_cost:.2f}"}
        },
        "total": {"currency": "USD", "value": f"{total:.2f}"},

        "available_payment_methods": ["CARD", "PAYPAL"]
    }

    CHECKOUT_SESSIONS[session_id] = session
    print(f"[UCP] 세션 생성됨: {session_id}")
    print(f"[UCP] 총액: ${total:.2f}")

    return jsonify({
        "success": True,
        "data": session
    })


@app.route("/ucp/checkout/submit", methods=["POST"])
def submit_order():
    """
    UCP Checkout: 주문 제출

    요청:
    {
        "session_id": "session_xxx",
        "payment": {
            "method": "CARD",
            "token": "tok_visa_xxx"
        },
        "shipping_address": {
            "recipient": "홍길동",
            "address_line": ["서울시 강남구 테헤란로 123"],
            "city": "서울",
            "postal_code": "06164",
            "country": "KR"
        }
    }
    """
    data = request.json or {}
    session_id = data.get("session_id")
    payment = data.get("payment", {})
    shipping_address = data.get("shipping_address", {})

    print(f"\n[UCP] 주문 제출: {session_id}")

    # 세션 확인
    session = CHECKOUT_SESSIONS.get(session_id)
    if not session:
        return jsonify({"success": False, "error": "Session not found"}), 404

    if session["status"] != "pending":
        return jsonify({"success": False, "error": "Session already processed"}), 400

    # 결제 처리 (시뮬레이션)
    print(f"[UCP] 결제 처리: {payment.get('method')}")

    # 주문 생성
    order_id = f"order_{uuid.uuid4().hex[:12]}"
    order = {
        "order_id": order_id,
        "status": "confirmed",
        "created_at": datetime.utcnow().isoformat() + "Z",

        "items": session["items"],
        "total": session["total"],
        "shipping_address": shipping_address,

        "payment": {
            "method": payment.get("method"),
            "status": "paid",
            "transaction_id": f"tx_{uuid.uuid4().hex[:12]}"
        },

        "estimated_delivery": "2026-01-28"
    }

    ORDERS[order_id] = order
    session["status"] = "completed"

    print(f"[UCP] 주문 완료: {order_id}")

    return jsonify({
        "success": True,
        "data": {
            "order": order,
            "message": "주문이 성공적으로 완료되었습니다"
        }
    })


# =============================================================================
# 서버 실행
# =============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("UCP 데모: 꽃집 서버")
    print("=" * 50)
    print(f"Capability Profile: http://localhost:5002/.well-known/ucp.json")
    print(f"Product Search: POST http://localhost:5002/ucp/discovery/search")
    print(f"Checkout: POST http://localhost:5002/ucp/checkout/session")
    print("=" * 50)
    app.run(port=5002, debug=True)
