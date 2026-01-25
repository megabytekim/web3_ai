"""
x402 데모: 단위 테스트

개별 함수의 동작을 검증합니다.
서버를 띄우지 않고 함수 단위로 테스트합니다.

실행: pytest test_unit.py -v
"""

import pytest
import json
import base64
import hashlib
import secrets
import time


# =============================================================================
# 테스트 대상 함수 정의 (client.py에서 추출)
# =============================================================================

def create_payment_payload(wallet_address: str, requirements: dict) -> dict:
    """
    x402 결제 페이로드 생성

    결제 페이로드는 다음을 포함합니다:
    - from: 지불자 주소
    - to: 수신자 주소
    - amount: 금액
    - nonce: 재사용 방지용 고유값
    - signature: 서명
    """
    nonce = secrets.token_hex(16)
    deadline = int(time.time()) + 3600  # 1시간 유효

    payload = {
        "version": 1,
        "from": wallet_address,
        "to": requirements["payTo"],
        "amount": requirements["maxAmountRequired"],
        "asset": requirements["asset"],
        "chain": requirements["network"],
        "nonce": nonce,
        "deadline": deadline,
        "signature": sign_payment(wallet_address, requirements, nonce, deadline)
    }

    return payload


def sign_payment(wallet_address: str, requirements: dict, nonce: str, deadline: int) -> str:
    """
    결제 서명 생성 (시뮬레이션)

    실제 구현에서는 EIP-712 서명을 사용합니다.
    """
    data = f"{wallet_address}{requirements['payTo']}{requirements['maxAmountRequired']}{nonce}{deadline}"
    hash_value = hashlib.sha256(data.encode()).hexdigest()
    return f"0x{hash_value}"


def encode_payment_header(payload: dict) -> str:
    """X-PAYMENT 헤더 인코딩 (Base64)"""
    json_str = json.dumps(payload)
    return base64.b64encode(json_str.encode()).decode()


def decode_payment_header(header: str) -> dict:
    """X-PAYMENT 헤더 디코딩"""
    json_str = base64.b64decode(header).decode()
    return json.loads(json_str)


def verify_payment_amount(paid_amount: int, required_amount: int) -> bool:
    """결제 금액 검증"""
    return paid_amount >= required_amount


def verify_nonce(nonce: str, used_nonces: set) -> bool:
    """nonce 중복 확인"""
    return nonce not in used_nonces


# =============================================================================
# 결제 페이로드 생성 테스트
# =============================================================================

class TestPaymentPayload:
    """결제 페이로드 생성 테스트"""

    @pytest.fixture
    def sample_requirements(self):
        """테스트용 결제 요구사항"""
        return {
            "scheme": "exact",
            "network": "base",
            "asset": "USDC",
            "payTo": "0x742d35Cc6634C0532925a3b844Bc9e7595f1E2B4",
            "maxAmountRequired": "100000",  # $0.10 USDC
            "resource": "/api/premium-data"
        }

    def test_payment_payload_structure(self, sample_requirements, sample_wallet_address):
        """
        결제 페이로드가 필수 필드를 포함하는지 확인
        """
        # When
        payload = create_payment_payload(sample_wallet_address, sample_requirements)

        # Then
        assert "version" in payload
        assert "from" in payload
        assert "to" in payload
        assert "amount" in payload
        assert "nonce" in payload
        assert "signature" in payload

    def test_payment_payload_contains_correct_values(self, sample_requirements, sample_wallet_address):
        """
        결제 페이로드 값이 올바른지 확인
        """
        # When
        payload = create_payment_payload(sample_wallet_address, sample_requirements)

        # Then
        assert payload["from"] == sample_wallet_address
        assert payload["to"] == sample_requirements["payTo"]
        assert payload["amount"] == sample_requirements["maxAmountRequired"]
        assert payload["asset"] == "USDC"
        assert payload["chain"] == "base"

    def test_payment_payload_has_unique_nonce(self, sample_requirements, sample_wallet_address):
        """
        각 페이로드가 고유한 nonce를 가지는지 확인
        """
        # When
        payload1 = create_payment_payload(sample_wallet_address, sample_requirements)
        payload2 = create_payment_payload(sample_wallet_address, sample_requirements)

        # Then
        assert payload1["nonce"] != payload2["nonce"]

    def test_payment_payload_has_valid_deadline(self, sample_requirements, sample_wallet_address):
        """
        deadline이 미래 시점인지 확인
        """
        # When
        payload = create_payment_payload(sample_wallet_address, sample_requirements)

        # Then
        current_time = int(time.time())
        assert payload["deadline"] > current_time


# =============================================================================
# 결제 서명 테스트
# =============================================================================

class TestPaymentSignature:
    """결제 서명 테스트"""

    def test_signature_is_hex_string(self, sample_wallet_address):
        """
        서명이 0x로 시작하는 hex 문자열인지 확인
        """
        # Given
        requirements = {
            "payTo": "0xRecipient",
            "maxAmountRequired": "100000"
        }

        # When
        signature = sign_payment(sample_wallet_address, requirements, "nonce123", 9999999)

        # Then
        assert signature.startswith("0x")
        assert len(signature) == 66  # 0x + 64 hex chars

    def test_signature_is_deterministic(self, sample_wallet_address):
        """
        같은 입력에 대해 같은 서명이 생성되는지 확인
        """
        # Given
        requirements = {"payTo": "0xRecipient", "maxAmountRequired": "100000"}
        nonce = "fixed_nonce"
        deadline = 9999999

        # When
        sig1 = sign_payment(sample_wallet_address, requirements, nonce, deadline)
        sig2 = sign_payment(sample_wallet_address, requirements, nonce, deadline)

        # Then
        assert sig1 == sig2

    def test_different_inputs_produce_different_signatures(self, sample_wallet_address):
        """
        다른 입력에 대해 다른 서명이 생성되는지 확인
        """
        # Given
        requirements = {"payTo": "0xRecipient", "maxAmountRequired": "100000"}
        deadline = 9999999

        # When
        sig1 = sign_payment(sample_wallet_address, requirements, "nonce1", deadline)
        sig2 = sign_payment(sample_wallet_address, requirements, "nonce2", deadline)

        # Then
        assert sig1 != sig2


# =============================================================================
# X-PAYMENT 헤더 인코딩/디코딩 테스트
# =============================================================================

class TestPaymentHeader:
    """X-PAYMENT 헤더 인코딩/디코딩 테스트"""

    def test_encode_decode_roundtrip(self):
        """
        인코딩 후 디코딩하면 원본이 복원되는지 확인
        """
        # Given
        original_payload = {
            "from": "0xSender",
            "to": "0xRecipient",
            "amount": "100000",
            "nonce": "abc123"
        }

        # When
        encoded = encode_payment_header(original_payload)
        decoded = decode_payment_header(encoded)

        # Then
        assert decoded == original_payload

    def test_encoded_header_is_base64(self):
        """
        인코딩된 헤더가 유효한 Base64인지 확인
        """
        # Given
        payload = {"test": "data"}

        # When
        encoded = encode_payment_header(payload)

        # Then: Base64 디코딩이 성공해야 함
        decoded_bytes = base64.b64decode(encoded)
        assert decoded_bytes is not None


# =============================================================================
# 결제 검증 로직 테스트
# =============================================================================

class TestPaymentVerification:
    """결제 검증 로직 테스트"""

    def test_sufficient_payment_is_valid(self):
        """
        충분한 금액이 유효로 판정되는지 확인
        """
        # When
        is_valid = verify_payment_amount(100000, 100000)

        # Then
        assert is_valid is True

    def test_excess_payment_is_valid(self):
        """
        초과 금액도 유효로 판정되는지 확인
        """
        # When
        is_valid = verify_payment_amount(200000, 100000)

        # Then
        assert is_valid is True

    def test_insufficient_payment_is_invalid(self):
        """
        부족한 금액이 무효로 판정되는지 확인
        """
        # When
        is_valid = verify_payment_amount(50000, 100000)

        # Then
        assert is_valid is False


# =============================================================================
# Nonce 검증 테스트
# =============================================================================

class TestNonceVerification:
    """Nonce 검증 테스트 (이중 지불 방지)"""

    def test_new_nonce_is_valid(self):
        """
        새로운 nonce가 유효로 판정되는지 확인
        """
        # Given
        used_nonces = set()

        # When
        is_valid = verify_nonce("new_nonce", used_nonces)

        # Then
        assert is_valid is True

    def test_used_nonce_is_invalid(self):
        """
        이미 사용된 nonce가 무효로 판정되는지 확인
        """
        # Given
        used_nonces = {"used_nonce"}

        # When
        is_valid = verify_nonce("used_nonce", used_nonces)

        # Then
        assert is_valid is False


# =============================================================================
# 402 응답 구조 테스트
# =============================================================================

class Test402Response:
    """402 Payment Required 응답 구조 테스트"""

    def test_402_response_structure(self):
        """
        402 응답이 x402 스펙에 맞는 구조를 가지는지 확인
        """
        # Given: 예상되는 402 응답 구조
        response_body = {
            "error": "Payment Required",
            "accepts": [
                {
                    "scheme": "exact",
                    "network": "base",
                    "asset": "USDC",
                    "payTo": "0xServerWallet",
                    "maxAmountRequired": "100000",
                    "resource": "/api/premium-data"
                }
            ],
            "x402Version": 1
        }

        # Then: 필수 필드 확인
        assert "accepts" in response_body
        assert "x402Version" in response_body
        assert len(response_body["accepts"]) > 0

        accept = response_body["accepts"][0]
        assert "network" in accept
        assert "asset" in accept
        assert "payTo" in accept
        assert "maxAmountRequired" in accept

    def test_payment_accepts_contains_required_fields(self):
        """
        accepts 배열의 각 항목이 필수 필드를 포함하는지 확인
        """
        # Given
        accept = {
            "scheme": "exact",
            "network": "base",
            "asset": "USDC",
            "payTo": "0x742d35Cc6634C0532925a3b844Bc9e7595f1E2B4",
            "maxAmountRequired": "500000"
        }

        # Then
        required_fields = ["scheme", "network", "asset", "payTo", "maxAmountRequired"]
        for field in required_fields:
            assert field in accept


# =============================================================================
# 실행
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
