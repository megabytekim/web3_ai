"""
x402 프로토콜 데모: 결제 클라이언트

이 클라이언트는 x402 프로토콜을 통해 유료 API에 접근합니다:
1. 402 응답 수신 및 파싱
2. 결제 페이로드 생성 및 서명
3. X-PAYMENT 헤더와 함께 재요청

공식 참고: https://github.com/coinbase/x402
"""

import httpx
import json
import base64
import hashlib
import secrets
import time

API_URL = "http://localhost:5003"


def main():
    print("=" * 50)
    print("x402 데모: 결제 클라이언트")
    print("=" * 50)

    client = X402Client(
        wallet_address="0xClientWallet1234567890abcdef",
        max_payment_per_call=1.0  # 호출당 최대 $1.00
    )

    # 무료 API 테스트
    print("\n[테스트 1] 무료 API 호출")
    client.call_api("/api/free-data")

    # 유료 API 테스트
    print("\n[테스트 2] 유료 API 호출 ($0.10)")
    client.call_api("/api/premium-data")

    # 더 비싼 API 테스트
    print("\n[테스트 3] AI 분석 API 호출 ($0.50)")
    client.call_api("/api/ai-analysis")


class X402Client:
    """
    x402 결제 클라이언트

    HTTP 402 응답을 자동으로 처리하고 결제합니다.
    """

    def __init__(self, wallet_address: str, max_payment_per_call: float = 1.0):
        self.wallet_address = wallet_address
        self.max_payment = max_payment_per_call
        self.http = httpx.Client(timeout=30.0)
        self.payment_history = []

    def call_api(self, endpoint: str) -> dict:
        """
        API 호출 (x402 자동 처리)

        402 응답 시 자동으로 결제를 처리하고 재요청합니다.
        """
        url = f"{API_URL}{endpoint}"
        print(f"  요청: GET {endpoint}")

        # 첫 번째 요청
        response = self.http.get(url)

        # 200 OK - 무료 또는 이미 결제됨
        if response.status_code == 200:
            print(f"  ✓ 성공 (무료)")
            data = response.json()
            print(f"  응답: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
            return data

        # 402 Payment Required
        if response.status_code == 402:
            print(f"  ⚠ 402 Payment Required")
            return self._handle_402(url, response)

        # 기타 에러
        print(f"  ❌ 에러: {response.status_code}")
        return None

    def _handle_402(self, url: str, response: httpx.Response) -> dict:
        """
        402 응답 처리

        1. 결제 요구사항 파싱
        2. 한도 확인
        3. 결제 페이로드 생성
        4. 재요청
        """
        # 결제 요구사항 파싱
        payment_req = self._parse_payment_requirements(response)
        if not payment_req:
            print("  ❌ 결제 요구사항 파싱 실패")
            return None

        # 결제 정보 출력
        amount_usdc = int(payment_req["maxAmountRequired"]) / 1_000_000
        print(f"  결제 요청:")
        print(f"    - 금액: ${amount_usdc:.2f} USDC")
        print(f"    - 네트워크: {payment_req['network']}")
        print(f"    - 수신 주소: {payment_req['payTo'][:20]}...")

        # 한도 확인
        if amount_usdc > self.max_payment:
            print(f"  ❌ 한도 초과: ${amount_usdc:.2f} > ${self.max_payment:.2f}")
            return None

        # 결제 페이로드 생성
        payment_payload = self._create_payment_payload(payment_req)
        payment_header = self._encode_payment_header(payment_payload)

        # 결제 헤더와 함께 재요청
        print(f"  → X-PAYMENT 헤더와 함께 재요청")
        response = self.http.get(url, headers={"X-PAYMENT": payment_header})

        if response.status_code == 200:
            print(f"  ✓ 결제 성공!")
            self._record_payment(url, payment_req, payment_payload)

            data = response.json()
            print(f"  응답: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}...")
            return data
        else:
            print(f"  ❌ 결제 후에도 실패: {response.status_code}")
            return None

    def _parse_payment_requirements(self, response: httpx.Response) -> dict:
        """402 응답에서 결제 요구사항 추출"""
        try:
            data = response.json()
            accepts = data.get("accepts", [])
            if accepts:
                return accepts[0]  # 첫 번째 옵션 사용
        except Exception as e:
            print(f"  파싱 오류: {e}")
        return None

    def _create_payment_payload(self, requirements: dict) -> dict:
        """
        x402 결제 페이로드 생성

        실제 구현에서는 EIP-712 서명을 사용합니다.
        """
        nonce = secrets.token_hex(16)
        deadline = int(time.time()) + 3600  # 1시간 유효

        payload = {
            "version": 1,
            "from": self.wallet_address,
            "to": requirements["payTo"],
            "amount": requirements["maxAmountRequired"],
            "asset": requirements["asset"],
            "chain": requirements["network"],
            "nonce": nonce,
            "deadline": deadline,
            "signature": self._sign_payment(requirements, nonce, deadline)
        }

        return payload

    def _sign_payment(self, requirements: dict, nonce: str, deadline: int) -> str:
        """
        결제 서명 생성 (시뮬레이션)

        실제 구현에서는:
        - EIP-712 타입 데이터 서명
        - 개인 키로 ECDSA 서명
        """
        data = f"{self.wallet_address}{requirements['payTo']}{requirements['maxAmountRequired']}{nonce}{deadline}"
        hash_value = hashlib.sha256(data.encode()).hexdigest()
        return f"0x{hash_value}"

    def _encode_payment_header(self, payload: dict) -> str:
        """X-PAYMENT 헤더 인코딩 (Base64)"""
        json_str = json.dumps(payload)
        return base64.b64encode(json_str.encode()).decode()

    def _record_payment(self, url: str, requirements: dict, payload: dict):
        """결제 기록 저장"""
        self.payment_history.append({
            "url": url,
            "amount": requirements["maxAmountRequired"],
            "asset": requirements["asset"],
            "network": requirements["network"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    def get_payment_summary(self) -> dict:
        """결제 요약"""
        total = sum(int(p["amount"]) for p in self.payment_history)
        return {
            "total_payments": len(self.payment_history),
            "total_usdc": total / 1_000_000,
            "history": self.payment_history
        }


if __name__ == "__main__":
    main()
