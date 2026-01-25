"""
x402 데모: 통합 테스트

실제 서버를 띄우고 x402의 전체 결제 플로우를 테스트합니다.

실행: pytest test_integration.py -v
"""

import pytest
import json
import base64
import secrets
import time
import hashlib
import sys
import os

# server 모듈 임포트
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server import app, USED_NONCES, PRICES, SERVER_WALLET


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
        # 각 테스트 전에 사용된 nonce 초기화
        USED_NONCES.clear()
        yield client


@pytest.fixture
def valid_payment_header():
    """유효한 결제 헤더 생성"""
    def create_header(resource: str = "/api/premium-data"):
        price = PRICES.get(resource, 100000)
        nonce = secrets.token_hex(16)
        deadline = int(time.time()) + 3600

        payload = {
            "version": 1,
            "from": "0xClientWallet1234567890abcdef",
            "to": SERVER_WALLET,
            "amount": str(price),
            "asset": "USDC",
            "chain": "base",
            "nonce": nonce,
            "deadline": deadline,
            "signature": f"0x{hashlib.sha256(f'{nonce}'.encode()).hexdigest()}"
        }

        return base64.b64encode(json.dumps(payload).encode()).decode()

    return create_header


# =============================================================================
# 무료 API 테스트
# =============================================================================

class TestFreeAPI:
    """
    무료 API 엔드포인트 테스트

    무료 API는 결제 없이 접근 가능합니다.
    """

    def test_free_api_returns_200(self, client):
        """
        무료 API가 200을 반환하는지 확인
        """
        # When
        response = client.get("/api/free-data")

        # Then
        assert response.status_code == 200

    def test_free_api_returns_data(self, client):
        """
        무료 API가 데이터를 반환하는지 확인
        """
        # When
        response = client.get("/api/free-data")
        data = json.loads(response.data)

        # Then
        assert "message" in data
        assert "timestamp" in data


# =============================================================================
# 402 응답 테스트
# =============================================================================

class Test402Response:
    """
    402 Payment Required 응답 테스트

    유료 API에 결제 헤더 없이 접근하면 402를 반환합니다.
    """

    def test_premium_api_without_payment_returns_402(self, client):
        """
        결제 헤더 없이 유료 API 접근 시 402 반환
        """
        # When
        response = client.get("/api/premium-data")

        # Then
        assert response.status_code == 402

    def test_402_response_contains_accepts(self, client):
        """
        402 응답에 accepts 배열이 포함되는지 확인
        """
        # When
        response = client.get("/api/premium-data")
        data = json.loads(response.data)

        # Then
        assert "accepts" in data
        assert len(data["accepts"]) > 0

    def test_402_response_contains_x402_version(self, client):
        """
        402 응답에 x402Version이 포함되는지 확인
        """
        # When
        response = client.get("/api/premium-data")
        data = json.loads(response.data)

        # Then
        assert "x402Version" in data
        assert data["x402Version"] == 1

    def test_402_response_specifies_payment_details(self, client):
        """
        402 응답이 결제 세부사항을 지정하는지 확인
        """
        # When
        response = client.get("/api/premium-data")
        data = json.loads(response.data)
        accept = data["accepts"][0]

        # Then
        assert accept["network"] == "base"
        assert accept["asset"] == "USDC"
        assert accept["payTo"] == SERVER_WALLET
        assert accept["maxAmountRequired"] == str(PRICES["/api/premium-data"])

    def test_different_endpoints_have_different_prices(self, client):
        """
        다른 엔드포인트가 다른 가격을 가지는지 확인
        """
        # When
        premium_response = client.get("/api/premium-data")
        ai_response = client.get("/api/ai-analysis")

        premium_data = json.loads(premium_response.data)
        ai_data = json.loads(ai_response.data)

        # Then
        premium_price = premium_data["accepts"][0]["maxAmountRequired"]
        ai_price = ai_data["accepts"][0]["maxAmountRequired"]

        assert premium_price == "100000"  # $0.10
        assert ai_price == "500000"       # $0.50


# =============================================================================
# 유효한 결제 테스트
# =============================================================================

class TestValidPayment:
    """
    유효한 결제 헤더를 포함한 요청 테스트
    """

    def test_valid_payment_returns_200(self, client, valid_payment_header):
        """
        유효한 결제 헤더로 요청 시 200 반환
        """
        # Given
        payment_header = valid_payment_header("/api/premium-data")

        # When
        response = client.get(
            "/api/premium-data",
            headers={"X-PAYMENT": payment_header}
        )

        # Then
        assert response.status_code == 200

    def test_valid_payment_returns_premium_data(self, client, valid_payment_header):
        """
        유효한 결제 후 프리미엄 데이터 반환
        """
        # Given
        payment_header = valid_payment_header("/api/premium-data")

        # When
        response = client.get(
            "/api/premium-data",
            headers={"X-PAYMENT": payment_header}
        )
        data = json.loads(response.data)

        # Then
        assert data["premium"] is True
        assert "data" in data

    def test_ai_analysis_endpoint_with_payment(self, client, valid_payment_header):
        """
        AI 분석 엔드포인트 결제 테스트
        """
        # Given
        payment_header = valid_payment_header("/api/ai-analysis")

        # When
        response = client.get(
            "/api/ai-analysis",
            headers={"X-PAYMENT": payment_header}
        )
        data = json.loads(response.data)

        # Then
        assert response.status_code == 200
        assert "analysis" in data


# =============================================================================
# 무효한 결제 테스트
# =============================================================================

class TestInvalidPayment:
    """
    무효한 결제 헤더 테스트
    """

    def test_invalid_base64_fails(self, client):
        """
        잘못된 Base64 인코딩이 실패하는지 확인
        """
        # When
        response = client.get(
            "/api/premium-data",
            headers={"X-PAYMENT": "not-valid-base64!!!"}
        )

        # Then
        assert response.status_code == 402

    def test_wrong_recipient_fails(self, client):
        """
        잘못된 수신 주소로 결제 시 실패
        """
        # Given
        payload = {
            "from": "0xClientWallet",
            "to": "0xWrongWallet",  # 잘못된 주소
            "amount": "100000",
            "nonce": secrets.token_hex(16),
            "signature": "0xfakesig"
        }
        payment_header = base64.b64encode(json.dumps(payload).encode()).decode()

        # When
        response = client.get(
            "/api/premium-data",
            headers={"X-PAYMENT": payment_header}
        )
        data = json.loads(response.data)

        # Then
        assert response.status_code == 402
        assert "Invalid recipient" in data.get("error", "")

    def test_insufficient_amount_fails(self, client):
        """
        금액 부족 시 실패
        """
        # Given
        payload = {
            "from": "0xClientWallet",
            "to": SERVER_WALLET,
            "amount": "50000",  # $0.05 - 부족
            "nonce": secrets.token_hex(16),
            "signature": "0xfakesig"
        }
        payment_header = base64.b64encode(json.dumps(payload).encode()).decode()

        # When
        response = client.get(
            "/api/premium-data",
            headers={"X-PAYMENT": payment_header}
        )
        data = json.loads(response.data)

        # Then
        assert response.status_code == 402
        assert "Insufficient payment" in data.get("error", "")

    def test_missing_signature_fails(self, client):
        """
        서명 누락 시 실패
        """
        # Given
        payload = {
            "from": "0xClientWallet",
            "to": SERVER_WALLET,
            "amount": "100000",
            "nonce": secrets.token_hex(16),
            # signature 없음
        }
        payment_header = base64.b64encode(json.dumps(payload).encode()).decode()

        # When
        response = client.get(
            "/api/premium-data",
            headers={"X-PAYMENT": payment_header}
        )
        data = json.loads(response.data)

        # Then
        assert response.status_code == 402
        assert "Missing signature" in data.get("error", "")


# =============================================================================
# Nonce 재사용 방지 테스트
# =============================================================================

class TestNonceReplay:
    """
    Nonce 재사용 방지 (이중 지불 방지) 테스트
    """

    def test_same_nonce_fails_on_second_use(self, client):
        """
        같은 nonce로 두 번 결제 시 두 번째가 실패
        """
        # Given: 고정된 nonce로 페이로드 생성
        fixed_nonce = "fixed_nonce_12345"
        payload = {
            "from": "0xClientWallet",
            "to": SERVER_WALLET,
            "amount": "100000",
            "nonce": fixed_nonce,
            "signature": "0xfakesig"
        }
        payment_header = base64.b64encode(json.dumps(payload).encode()).decode()

        # When: 첫 번째 요청 (성공해야 함)
        response1 = client.get(
            "/api/premium-data",
            headers={"X-PAYMENT": payment_header}
        )

        # When: 두 번째 요청 (실패해야 함)
        response2 = client.get(
            "/api/premium-data",
            headers={"X-PAYMENT": payment_header}
        )

        # Then
        assert response1.status_code == 200
        assert response2.status_code == 402

        data2 = json.loads(response2.data)
        assert "Nonce already used" in data2.get("error", "")


# =============================================================================
# 전체 결제 플로우 테스트
# =============================================================================

class TestFullPaymentFlow:
    """
    전체 x402 결제 플로우 테스트

    1. 유료 API 요청 → 402 수신
    2. 결제 요구사항 파싱
    3. 결제 페이로드 생성
    4. X-PAYMENT 헤더와 함께 재요청 → 200 수신
    """

    def test_complete_payment_flow(self, client):
        """
        전체 결제 플로우가 성공적으로 완료되는지 확인
        """
        # Step 1: 첫 요청 (402 예상)
        response1 = client.get("/api/premium-data")
        assert response1.status_code == 402
        print("\n1. 402 Payment Required 수신")

        # Step 2: 결제 요구사항 파싱
        payment_req = json.loads(response1.data)
        accept = payment_req["accepts"][0]

        print(f"2. 결제 요구사항:")
        print(f"   - 금액: {int(accept['maxAmountRequired']) / 1_000_000:.2f} USDC")
        print(f"   - 네트워크: {accept['network']}")
        print(f"   - 수신 주소: {accept['payTo'][:20]}...")

        # Step 3: 결제 페이로드 생성
        nonce = secrets.token_hex(16)
        payload = {
            "version": 1,
            "from": "0xTestClientWallet",
            "to": accept["payTo"],
            "amount": accept["maxAmountRequired"],
            "asset": accept["asset"],
            "chain": accept["network"],
            "nonce": nonce,
            "deadline": int(time.time()) + 3600,
            "signature": f"0x{hashlib.sha256(nonce.encode()).hexdigest()}"
        }

        payment_header = base64.b64encode(json.dumps(payload).encode()).decode()
        print(f"3. 결제 페이로드 생성 완료")

        # Step 4: X-PAYMENT 헤더와 함께 재요청
        response2 = client.get(
            "/api/premium-data",
            headers={"X-PAYMENT": payment_header}
        )

        # 최종 확인
        assert response2.status_code == 200
        data = json.loads(response2.data)
        assert data["premium"] is True

        print(f"4. 결제 성공! 프리미엄 데이터 수신")
        print(f"   ✓ 프리미엄: {data['premium']}")
        print(f"   ✓ 트렌드 점수: {data['data']['trend_score']}")

    def test_multiple_sequential_payments(self, client, valid_payment_header):
        """
        여러 번의 순차 결제가 모두 성공하는지 확인
        """
        # 첫 번째 결제
        response1 = client.get(
            "/api/premium-data",
            headers={"X-PAYMENT": valid_payment_header("/api/premium-data")}
        )
        assert response1.status_code == 200

        # 두 번째 결제 (새로운 nonce)
        response2 = client.get(
            "/api/ai-analysis",
            headers={"X-PAYMENT": valid_payment_header("/api/ai-analysis")}
        )
        assert response2.status_code == 200

        print("\n✓ 2개의 순차 결제 모두 성공!")


# =============================================================================
# 실행
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
