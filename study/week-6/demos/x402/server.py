"""
x402 프로토콜 데모: 유료 API 서버

이 서버는 x402 프로토콜의 핵심 개념을 시뮬레이션합니다:
- 402 Payment Required 응답
- X-PAYMENT 헤더 검증
- 결제 후 리소스 제공

공식 참고: https://github.com/coinbase/x402
"""

from flask import Flask, jsonify, request, Response
import json
import base64
import hashlib

app = Flask(__name__)

# =============================================================================
# 설정
# =============================================================================

# 서버 지갑 주소 (수신용)
SERVER_WALLET = "0x742d35Cc6634C0532925a3b844Bc9e7595f1E2B4"

# 가격 설정 (USDC, 6 decimals)
PRICES = {
    "/api/premium-data": 100000,      # $0.10 USDC
    "/api/ai-analysis": 500000,       # $0.50 USDC
    "/api/full-report": 1000000,      # $1.00 USDC
}

# 처리된 nonce (이중 지불 방지)
USED_NONCES = set()


# =============================================================================
# 무료 엔드포인트
# =============================================================================

@app.route("/api/free-data", methods=["GET"])
def free_data():
    """무료 API - 결제 불필요"""
    return jsonify({
        "message": "This is free data!",
        "timestamp": "2026-01-25T12:00:00Z"
    })


# =============================================================================
# 유료 엔드포인트 (x402)
# =============================================================================

@app.route("/api/premium-data", methods=["GET"])
def premium_data():
    """
    유료 API - x402 결제 필요

    1. X-PAYMENT 헤더가 없으면 → 402 반환
    2. X-PAYMENT 헤더가 있으면 → 검증 후 데이터 반환
    """
    payment_header = request.headers.get("X-PAYMENT")

    if not payment_header:
        # 402 Payment Required 반환
        return create_402_response("/api/premium-data")

    # 결제 검증
    is_valid, error = verify_payment(payment_header, "/api/premium-data")

    if not is_valid:
        return jsonify({"error": error}), 402

    # 결제 성공 - 프리미엄 데이터 반환
    print("[x402] 결제 확인됨, 데이터 제공")
    return jsonify({
        "premium": True,
        "data": {
            "market_analysis": "AI agents are transforming commerce...",
            "trend_score": 95,
            "recommendations": [
                "Invest in agentic infrastructure",
                "Monitor UCP adoption",
                "Prepare for AP2 integration"
            ]
        },
        "access_granted_at": "2026-01-25T12:00:00Z"
    })


@app.route("/api/ai-analysis", methods=["GET"])
def ai_analysis():
    """유료 API - AI 분석 ($0.50)"""
    payment_header = request.headers.get("X-PAYMENT")

    if not payment_header:
        return create_402_response("/api/ai-analysis")

    is_valid, error = verify_payment(payment_header, "/api/ai-analysis")
    if not is_valid:
        return jsonify({"error": error}), 402

    return jsonify({
        "analysis": {
            "sentiment": "positive",
            "confidence": 0.87,
            "summary": "The agentic commerce market shows strong growth potential."
        }
    })


# =============================================================================
# x402: 402 응답 생성
# =============================================================================

def create_402_response(resource: str):
    """
    x402 Payment Required 응답 생성

    이 응답은 클라이언트에게 결제 조건을 알려줍니다:
    - 어떤 네트워크/자산을 받는지
    - 얼마를 받는지
    - 어디로 보내야 하는지
    """
    price = PRICES.get(resource, 100000)

    print(f"\n[x402] 402 Payment Required: {resource}")
    print(f"[x402] 요청 금액: {price / 1_000_000:.2f} USDC")

    response_body = {
        "error": "Payment Required",
        "accepts": [
            {
                # 결제 방식
                "scheme": "exact",

                # 블록체인 네트워크
                "network": "base",

                # 결제 자산 (USDC)
                "asset": "USDC",

                # 수신 주소
                "payTo": SERVER_WALLET,

                # 필요 금액 (USDC는 6 decimals)
                "maxAmountRequired": str(price),

                # 결제 대상 리소스
                "resource": resource,

                # 설명
                "description": f"Access to {resource}",

                # 추가 정보
                "extra": {
                    "name": "x402 Demo Server",
                    "version": "1.0"
                }
            }
        ],
        "x402Version": 1
    }

    return Response(
        json.dumps(response_body),
        status=402,
        mimetype="application/json"
    )


# =============================================================================
# x402: 결제 검증
# =============================================================================

def verify_payment(payment_header: str, resource: str) -> tuple:
    """
    X-PAYMENT 헤더 검증

    실제 구현에서는:
    1. 서명 검증 (EIP-712)
    2. 금액 확인
    3. nonce 중복 확인
    4. deadline 확인
    5. Facilitator를 통한 온체인 검증

    이 데모에서는 시뮬레이션으로 처리합니다.
    """
    try:
        # Base64 디코딩
        payload_json = base64.b64decode(payment_header).decode()
        payload = json.loads(payload_json)

        print(f"\n[x402] 결제 검증 중...")
        print(f"[x402] From: {payload.get('from', 'N/A')[:20]}...")
        print(f"[x402] Amount: {int(payload.get('amount', 0)) / 1_000_000:.2f} USDC")

        # 1. 수신 주소 확인
        if payload.get("to") != SERVER_WALLET:
            return False, "Invalid recipient address"

        # 2. 금액 확인
        required_amount = PRICES.get(resource, 100000)
        paid_amount = int(payload.get("amount", 0))
        if paid_amount < required_amount:
            return False, f"Insufficient payment: {paid_amount} < {required_amount}"

        # 3. nonce 중복 확인 (이중 지불 방지)
        nonce = payload.get("nonce")
        if nonce in USED_NONCES:
            return False, "Nonce already used"
        USED_NONCES.add(nonce)

        # 4. deadline 확인 (시뮬레이션에서는 스킵)

        # 5. 서명 검증 (시뮬레이션에서는 서명이 있는지만 확인)
        if not payload.get("signature"):
            return False, "Missing signature"

        print("[x402] 결제 검증 성공!")
        return True, None

    except Exception as e:
        return False, f"Invalid payment header: {str(e)}"


# =============================================================================
# 서버 실행
# =============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("x402 데모: 유료 API 서버")
    print("=" * 50)
    print(f"무료 API: http://localhost:5003/api/free-data")
    print(f"유료 API: http://localhost:5003/api/premium-data ($0.10)")
    print(f"유료 API: http://localhost:5003/api/ai-analysis ($0.50)")
    print(f"서버 지갑: {SERVER_WALLET}")
    print("=" * 50)
    app.run(port=5003, debug=True)
