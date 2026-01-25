"""
A2A + AP2 데모: 판매자 에이전트 (Merchant Agent)

이 서버는 A2A 프로토콜의 핵심 엔드포인트와
AP2의 Mandate 시스템을 시뮬레이션합니다.

공식 참고: https://github.com/a2aproject/a2a-samples
"""

from flask import Flask, jsonify, request
from datetime import datetime
import uuid

app = Flask(__name__)

# =============================================================================
# 샘플 데이터
# =============================================================================

PRODUCTS = [
    {"id": "nike-001", "name": "Nike Air Max 90 (Red)", "price": 120.00, "currency": "USD"},
    {"id": "nike-002", "name": "Nike Air Force 1 (White)", "price": 110.00, "currency": "USD"},
    {"id": "adidas-001", "name": "Adidas Ultraboost (Black)", "price": 180.00, "currency": "USD"},
]

TASKS = {}  # 메모리 내 태스크 저장소


# =============================================================================
# A2A: Agent Card (에이전트 발견)
# =============================================================================

@app.route("/.well-known/agent-card.json", methods=["GET"])
def agent_card():
    """
    A2A 에이전트 카드 - 에이전트의 신원과 기능을 선언

    클라이언트는 이 엔드포인트를 통해 에이전트를 발견하고
    어떤 기능(skills)과 확장(extensions)을 지원하는지 확인합니다.
    """
    return jsonify({
        "protocolVersion": "0.3.0",
        "name": "Demo Merchant Agent",
        "description": "A2A + AP2 데모용 판매자 에이전트",
        "url": "http://localhost:5001/a2a",

        # 에이전트가 제공하는 기능
        "skills": [
            {
                "id": "product-search",
                "name": "상품 검색",
                "description": "키워드로 상품을 검색합니다",
                "tags": ["commerce", "search"]
            },
            {
                "id": "checkout",
                "name": "결제 처리",
                "description": "AP2 Mandate를 통한 안전한 결제",
                "tags": ["commerce", "payment", "ap2"]
            }
        ],

        # AP2 지원 선언 (중요!)
        "extensions": [
            {
                "uri": "https://google-a2a.github.io/A2A/extensions/payments/v1",
                "description": "AP2 결제 프로토콜 지원"
            }
        ],

        # 결제 수단
        "paymentCapabilities": {
            "supportedMethods": ["CARD", "CRYPTO"],
            "supportedCurrencies": ["USD"]
        }
    })


# =============================================================================
# A2A: JSON-RPC 엔드포인트
# =============================================================================

@app.route("/a2a", methods=["POST"])
def a2a_endpoint():
    """
    A2A JSON-RPC 엔드포인트

    지원 메서드:
    - tasks/create: 새 태스크 생성
    - tasks/get: 태스크 상태 조회
    - message/send: 메시지 전송 (Payment Mandate 등)
    """
    data = request.json
    method = data.get("method")
    params = data.get("params", {})
    request_id = data.get("id", str(uuid.uuid4()))

    print(f"\n[Merchant] 수신: {method}")

    if method == "tasks/create":
        return handle_task_create(params, request_id)
    elif method == "tasks/get":
        return handle_task_get(params, request_id)
    elif method == "message/send":
        return handle_message_send(params, request_id)
    else:
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Unknown method: {method}"}
        })


def handle_task_create(params, request_id):
    """
    태스크 생성 - 상품 검색 요청 처리

    클라이언트가 검색 요청을 보내면:
    1. 상품 검색 수행
    2. Cart Mandate (장바구니 확인 요청) 생성
    3. 태스크에 Artifact로 첨부하여 반환
    """
    task_id = params.get("taskId", f"task_{uuid.uuid4().hex[:8]}")
    message = params.get("message", {})

    # 검색어 추출
    search_query = ""
    for part in message.get("parts", []):
        if part.get("kind") == "text":
            search_query = part.get("text", "")
            break

    print(f"[Merchant] 검색어: {search_query}")

    # 간단한 검색 (실제로는 더 정교한 로직)
    matching_products = [p for p in PRODUCTS if "red" in search_query.lower() or "빨간" in search_query]
    if not matching_products:
        matching_products = PRODUCTS[:1]  # 기본값

    selected_product = matching_products[0]

    # =================================================================
    # AP2: Cart Mandate 생성 (핵심!)
    # =================================================================
    cart_mandate = create_cart_mandate(selected_product)

    # 태스크 생성 및 저장
    task = {
        "id": task_id,
        "contextId": params.get("contextId", f"ctx_{uuid.uuid4().hex[:8]}"),
        "status": {"state": "input-required"},  # 사용자 입력(결제 승인) 대기
        "artifacts": [
            {
                "artifactId": f"cart_{uuid.uuid4().hex[:8]}",
                "parts": [
                    {
                        "kind": "data",
                        "data": {
                            "ap2.mandates.CartMandate": cart_mandate
                        }
                    }
                ]
            }
        ],
        "product": selected_product  # 데모용 추가 정보
    }

    TASKS[task_id] = task
    print(f"[Merchant] Cart Mandate 생성 완료")

    return jsonify({
        "jsonrpc": "2.0",
        "id": request_id,
        "result": task
    })


def handle_task_get(params, request_id):
    """태스크 상태 조회"""
    task_id = params.get("taskId")
    task = TASKS.get(task_id)

    if not task:
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32602, "message": "Task not found"}
        })

    return jsonify({
        "jsonrpc": "2.0",
        "id": request_id,
        "result": task
    })


def handle_message_send(params, request_id):
    """
    메시지 수신 - Payment Mandate 처리

    클라이언트가 Payment Mandate를 보내면:
    1. 서명 검증 (시뮬레이션)
    2. 결제 처리 (시뮬레이션)
    3. 태스크 상태를 'completed'로 변경
    """
    task_id = params.get("taskId")
    message = params.get("message", {})

    task = TASKS.get(task_id)
    if not task:
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32602, "message": "Task not found"}
        })

    # Payment Mandate 추출
    payment_mandate = None
    for part in message.get("parts", []):
        if part.get("kind") == "data":
            payment_mandate = part.get("data", {}).get("ap2.mandates.PaymentMandate")
            break

    if payment_mandate:
        print(f"[Merchant] Payment Mandate 수신")
        print(f"[Merchant] Mandate ID: {payment_mandate.get('payment_mandate_contents', {}).get('payment_mandate_id')}")

        # =================================================================
        # AP2: Payment Mandate 검증 (시뮬레이션)
        # =================================================================
        is_valid = verify_payment_mandate(payment_mandate)

        if is_valid:
            # 결제 성공 - 태스크 완료
            task["status"] = {
                "state": "completed",
                "transactionId": f"tx_{uuid.uuid4().hex[:12]}",
                "message": "결제가 완료되었습니다"
            }
            print(f"[Merchant] 결제 완료: {task['status']['transactionId']}")
        else:
            task["status"] = {
                "state": "failed",
                "message": "결제 검증 실패"
            }

    return jsonify({
        "jsonrpc": "2.0",
        "id": request_id,
        "result": task
    })


# =============================================================================
# AP2: Mandate 관련 함수
# =============================================================================

def create_cart_mandate(product):
    """
    AP2 Cart Mandate 생성

    Cart Mandate는 판매자가 구매자에게 보내는 '장바구니 확인 요청'입니다.
    구매자는 이를 확인하고 Payment Mandate로 승인합니다.
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
    AP2 Payment Mandate 검증 (시뮬레이션)

    실제 구현에서는:
    1. 사용자 서명 검증 (ECDSA 등)
    2. Agent Presence Indicator 확인
    3. 결제 정보 유효성 검증
    """
    # 시뮬레이션: 항상 성공
    user_auth = payment_mandate.get("user_authorization")
    return user_auth is not None and len(user_auth) > 0


# =============================================================================
# 서버 실행
# =============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("A2A + AP2 데모: 판매자 에이전트")
    print("=" * 50)
    print(f"Agent Card: http://localhost:5001/.well-known/agent-card.json")
    print(f"A2A Endpoint: http://localhost:5001/a2a")
    print("=" * 50)
    app.run(port=5001, debug=True)
