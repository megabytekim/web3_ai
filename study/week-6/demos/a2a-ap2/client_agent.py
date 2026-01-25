"""
A2A + AP2 데모: 쇼핑 에이전트 (Client Agent)

이 클라이언트는 A2A 프로토콜을 통해 판매자 에이전트와 통신하고
AP2 Mandate 시스템을 통해 결제를 수행합니다.

공식 참고: https://github.com/a2aproject/a2a-samples
"""

import httpx
import uuid
import json
import time

MERCHANT_URL = "http://localhost:5001"


def main():
    print("=" * 50)
    print("A2A + AP2 데모: 쇼핑 에이전트")
    print("=" * 50)

    client = ShoppingAgent()

    # 전체 구매 플로우 실행
    client.run_purchase_flow("빨간 운동화 찾아줘")


class ShoppingAgent:
    """
    쇼핑 에이전트 - 사용자를 대신하여 상품을 검색하고 구매
    """

    def __init__(self):
        self.http = httpx.Client(timeout=30.0)
        self.user_credentials = {
            "userId": "user_demo_123",
            "name": "홍길동",
            "email": "hong@example.com",
            "paymentToken": "tok_visa_demo_4242"
        }

    def run_purchase_flow(self, search_query: str):
        """전체 구매 플로우 실행"""

        print(f"\n검색 요청: \"{search_query}\"\n")

        # =========================================================
        # Step 1: 에이전트 발견 (Agent Discovery)
        # =========================================================
        print("[Step 1] 에이전트 발견")
        agent_card = self.discover_agent()
        if not agent_card:
            print("  ❌ 에이전트를 찾을 수 없습니다")
            return

        print(f"  ✓ 이름: {agent_card['name']}")

        # AP2 지원 여부 확인
        supports_ap2 = any(
            "payments" in ext.get("uri", "")
            for ext in agent_card.get("extensions", [])
        )
        print(f"  ✓ AP2 지원: {supports_ap2}")

        if not supports_ap2:
            print("  ❌ 이 에이전트는 AP2를 지원하지 않습니다")
            return

        # =========================================================
        # Step 2: 검색 태스크 생성
        # =========================================================
        print("\n[Step 2] 검색 태스크 생성")
        task = self.create_search_task(search_query)
        if not task:
            print("  ❌ 태스크 생성 실패")
            return

        print(f"  ✓ Task ID: {task['id']}")
        print(f"  ✓ 상태: {task['status']['state']}")

        # =========================================================
        # Step 3: Cart Mandate 수신 및 확인
        # =========================================================
        print("\n[Step 3] Cart Mandate 수신")
        cart_mandate = self.extract_cart_mandate(task)
        if not cart_mandate:
            print("  ❌ Cart Mandate를 찾을 수 없습니다")
            return

        # 장바구니 내용 표시
        details = cart_mandate["contents"]["payment_request"]["details"]
        for item in details.get("displayItems", []):
            print(f"  ✓ 상품: {item['label']}")
            print(f"  ✓ 가격: {item['amount']['currency']} {item['amount']['value']}")

        total = details["total"]["amount"]
        print(f"  ✓ 총액: {total['currency']} {total['value']}")

        # =========================================================
        # Step 4: Payment Mandate 생성 및 전송
        # =========================================================
        print("\n[Step 4] Payment Mandate 생성")

        # 사용자 승인 시뮬레이션
        print("  [시뮬레이션] 사용자가 결제를 승인했습니다")

        payment_mandate = self.create_payment_mandate(cart_mandate)
        print(f"  ✓ Mandate ID: {payment_mandate['payment_mandate_contents']['payment_mandate_id']}")

        # Agent Presence Indicator (중요!)
        api = payment_mandate["agent_presence_indicator"]
        print(f"  ✓ Agent Initiated: {api['agent_initiated']}")
        print(f"  ✓ Human Present: {api['human_present']}")

        # =========================================================
        # Step 5: 결제 실행
        # =========================================================
        print("\n[Step 5] 결제 실행")
        result = self.execute_payment(task["id"], task["contextId"], payment_mandate)

        if result and result.get("status", {}).get("state") == "completed":
            print(f"  ✓ 결제 완료!")
            print(f"  ✓ Transaction ID: {result['status'].get('transactionId')}")
        else:
            print(f"  ❌ 결제 실패")

        print("\n" + "=" * 50)
        print("데모 종료")
        print("=" * 50)

    # =================================================================
    # A2A 통신 메서드
    # =================================================================

    def discover_agent(self) -> dict:
        """
        A2A: 에이전트 발견

        /.well-known/agent-card.json 엔드포인트에서
        에이전트의 신원과 기능을 조회합니다.
        """
        try:
            response = self.http.get(f"{MERCHANT_URL}/.well-known/agent-card.json")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"  오류: {e}")
        return None

    def create_search_task(self, query: str) -> dict:
        """
        A2A: 검색 태스크 생성

        JSON-RPC를 통해 tasks/create 메서드를 호출합니다.
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        context_id = f"ctx_{uuid.uuid4().hex[:8]}"

        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/create",
            "params": {
                "taskId": task_id,
                "contextId": context_id,
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "user",
                    "parts": [
                        {"kind": "text", "text": query}
                    ]
                }
            }
        }

        try:
            response = self.http.post(
                f"{MERCHANT_URL}/a2a",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            return result.get("result")
        except Exception as e:
            print(f"  오류: {e}")
        return None

    def extract_cart_mandate(self, task: dict) -> dict:
        """
        AP2: Cart Mandate 추출

        태스크의 artifacts에서 Cart Mandate를 찾습니다.
        """
        for artifact in task.get("artifacts", []):
            for part in artifact.get("parts", []):
                if part.get("kind") == "data":
                    cart_mandate = part.get("data", {}).get("ap2.mandates.CartMandate")
                    if cart_mandate:
                        return cart_mandate
        return None

    def create_payment_mandate(self, cart_mandate: dict) -> dict:
        """
        AP2: Payment Mandate 생성

        Cart Mandate를 기반으로 Payment Mandate를 생성합니다.
        실제 구현에서는 사용자의 하드웨어 키로 서명합니다.
        """
        cart_contents = cart_mandate["contents"]
        mandate_id = f"pm_{uuid.uuid4().hex[:12]}"

        payment_mandate = {
            "payment_mandate_contents": {
                "payment_mandate_id": mandate_id,
                "payment_details_id": cart_contents["payment_request"]["details"]["id"],
                "payment_details_total": cart_contents["payment_request"]["details"]["total"],
                "payment_response": {
                    "request_id": cart_contents["id"],
                    "method_name": "CARD",
                    "details": {
                        "token": self.user_credentials["paymentToken"],
                        "tokenized": True
                    }
                },
                "merchant_agent": "Demo Merchant Agent",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            },

            # 사용자 서명 (시뮬레이션)
            "user_authorization": self._sign_mandate(cart_mandate),

            # Agent Presence Indicator (AP2 핵심!)
            # 이 정보는 결제 사기 방지에 중요합니다
            "agent_presence_indicator": {
                "agent_initiated": True,      # 에이전트가 시작한 거래
                "human_present": True,        # 사람이 승인함
                "agent_id": "shopping-agent-demo",
                "agent_provider": "Demo Shopping Agent"
            }
        }

        return payment_mandate

    def execute_payment(self, task_id: str, context_id: str, payment_mandate: dict) -> dict:
        """
        A2A: Payment Mandate 전송

        message/send 메서드를 통해 Payment Mandate를 전송합니다.
        """
        payload = {
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
                                "ap2.mandates.PaymentMandate": payment_mandate
                            }
                        }
                    ]
                }
            }
        }

        try:
            response = self.http.post(
                f"{MERCHANT_URL}/a2a",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            return result.get("result")
        except Exception as e:
            print(f"  오류: {e}")
        return None

    def _sign_mandate(self, data: dict) -> str:
        """
        서명 생성 (시뮬레이션)

        실제 구현에서는:
        - WebAuthn / FIDO2
        - 하드웨어 보안 모듈 (HSM)
        - ECDSA 서명
        """
        import hashlib
        import base64

        payload = json.dumps(data, sort_keys=True)
        hash_value = hashlib.sha256(payload.encode()).hexdigest()
        return f"eyJhbGciOiJFUzI1NksifQ.{base64.b64encode(hash_value.encode()).decode()[:30]}"


if __name__ == "__main__":
    main()
