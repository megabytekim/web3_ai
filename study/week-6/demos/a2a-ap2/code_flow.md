# A2A + AP2 코드 플로우

## AP2 공식 스펙 요약

> **출처**: [AP2 Protocol Specification](https://ap2-protocol.org/specification/)

AP2는 Google이 PayPal, Mastercard, American Express, Coinbase 등 60개 이상의 기업과 협력하여 만든 **AI 에이전트 결제 프로토콜**입니다.

### 3가지 Mandate 체계

| Mandate | 생성자 | 서명자 | 사용 시나리오 |
|---------|--------|--------|--------------|
| **Cart Mandate** | Merchant | **User** | Human Present (사람이 확인) |
| **Intent Mandate** | Agent | **User** | Human NOT Present (사전 위임) |
| **Payment Mandate** | Agent | Agent | 결제 네트워크에 AI 관여 알림 |

### Cart Mandate vs Intent Mandate

```
Human Present (실시간 확인)          Human NOT Present (사전 위임)
─────────────────────────          ─────────────────────────────
"운동화 찾아줘"                     "콘서트 티켓 풀리면 바로 사줘"
     ↓                                   ↓
Agent가 상품 검색                    User가 Intent Mandate 서명
     ↓                              (조건: 가격 < $200, 좌석 A구역)
Merchant가 Cart Mandate 생성              ↓
     ↓                              티켓 오픈 시 Agent가 자동 구매
User가 Cart Mandate 서명                  ↓
     ↓                              Cart Mandate 자동 생성
결제 진행                            (Intent 조건 충족 시)
```

---

## 핵심 개념

### Task = 세션

A2A에서 **Task**는 하나의 거래 세션입니다. 검색부터 결제 완료까지 동일한 Task 안에서 진행됩니다.

```
Task (task_abc123)
├── 상태: submitted → working → input-required → completed
├── contextId: 대화 컨텍스트 (여러 Task가 공유 가능)
├── artifacts: Cart Mandate 등 첨부 데이터
└── 메시지들이 순차적으로 쌓임
```

### Mandate 플로우 (Human Present)

```
┌─────────────┐                           ┌─────────────┐
│   User +    │                           │   Merchant  │
│   Agent     │                           │   Agent     │
└──────┬──────┘                           └──────┬──────┘
       │                                         │
       │  "빨간 운동화 찾아줘"                     │
       │ ───────────────────────────────────────▶│
       │                                         │
       │         Cart Mandate (미서명)            │
       │ ◀───────────────────────────────────────│
       │   Merchant가 생성, User 서명 요청         │
       │                                         │
       │  [User가 Cart Mandate 확인 및 서명]       │
       │                                         │
       │         Payment Mandate                 │
       │         + 서명된 Cart Mandate            │
       │ ───────────────────────────────────────▶│
       │   Agent가 생성, AI 관여 정보 포함         │
       │                                         │
       │         결제 완료                        │
       │ ◀───────────────────────────────────────│
       │                                         │
```

---

## 전체 플로우 (A2A + AP2)

```
┌─────────────┐                           ┌─────────────┐
│   Buyer     │                           │   Merchant  │
│  (client)   │                           │   (server)  │
└──────┬──────┘                           └──────┬──────┘
       │                                         │
  [1]  │  GET /.well-known/agent-card.json       │
       │ ───────────────────────────────────────▶│
       │                                         │
       │  Agent Card (skills, AP2 지원 여부)       │
       │ ◀───────────────────────────────────────│
       │                                         │
  [2]  │  POST /a2a                              │
       │  method: "tasks/create"                 │
       │  message: "빨간 운동화 찾아줘"             │
       │ ───────────────────────────────────────▶│
       │                                         │
       │  Task + Cart Mandate                    │
       │  status: "input-required"               │
       │ ◀───────────────────────────────────────│
       │                                         │
  [3]  │  (사용자가 Cart Mandate 확인 및 서명)      │
       │                                         │
  [4]  │  POST /a2a                              │
       │  method: "message/send"                 │
       │  taskId: 동일한 Task ID                  │
       │  Payment Mandate + 서명                  │
       │ ───────────────────────────────────────▶│
       │                                         │
       │  Task (status: "completed")             │
       │  transactionId: "tx_..."                │
       │ ◀───────────────────────────────────────│
       │                                         │
```

---

## 코드 매핑

### Step 1: Agent Card 조회

**client_agent.py**
```python
response = self.http.get(f"{self.merchant_url}/.well-known/agent-card.json")
agent_card = response.json()

# AP2 지원 확인
supports_ap2 = any("payments" in ext.get("uri", "") for ext in agent_card.get("extensions", []))
```

**merchant_agent.py** (33-76줄)
```python
@app.route("/.well-known/agent-card.json", methods=["GET"])
def agent_card():
    return jsonify({
        "protocolVersion": "0.3.0",
        "name": "Demo Merchant Agent",
        "skills": [...],
        "extensions": [
            {"uri": "https://google-a2a.github.io/A2A/extensions/payments/v1"}  # AP2!
        ]
    })
```

### Step 2: Task 생성 → Cart Mandate 수신

**client_agent.py**
```python
response = self.http.post(f"{self.merchant_url}/a2a", json={
    "jsonrpc": "2.0",
    "method": "tasks/create",
    "params": {
        "taskId": task_id,
        "message": {"parts": [{"kind": "text", "text": "빨간 운동화 찾아줘"}]}
    }
})
task = response.json()["result"]
# task["status"]["state"] == "input-required"
# task["artifacts"][0]["parts"][0]["data"]["ap2.mandates.CartMandate"]
```

**merchant_agent.py** (114-175줄)
```python
def handle_task_create(params, request_id):
    # 1. 검색어 추출
    search_query = message["parts"][0]["text"]

    # 2. 상품 검색
    selected_product = PRODUCTS[0]

    # 3. Cart Mandate 생성
    cart_mandate = create_cart_mandate(selected_product)

    # 4. Task 저장 (status: input-required)
    task = {
        "id": task_id,
        "status": {"state": "input-required"},
        "artifacts": [{
            "parts": [{
                "kind": "data",
                "data": {"ap2.mandates.CartMandate": cart_mandate}
            }]
        }]
    }
    TASKS[task_id] = task  # 메모리에 저장
```

### Step 3-4: Payment Mandate 전송 → 결제 완료

**client_agent.py**
```python
payment_mandate = {
    "payment_mandate_contents": {"payment_mandate_id": "pm_xxx"},
    "user_authorization": "사용자_서명",  # 핵심!
    "agent_presence_indicator": {
        "agent_initiated": True,
        "human_present": True
    }
}

response = self.http.post(f"{self.merchant_url}/a2a", json={
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
        "taskId": task_id,  # 동일한 Task!
        "message": {"parts": [{"kind": "data", "data": {"ap2.mandates.PaymentMandate": payment_mandate}}]}
    }
})
# result["status"]["state"] == "completed"
# result["status"]["transactionId"] == "tx_..."
```

**merchant_agent.py** (197-251줄)
```python
def handle_message_send(params, request_id):
    task_id = params.get("taskId")
    task = TASKS.get(task_id)  # 기존 Task 조회

    # Payment Mandate 추출
    payment_mandate = message["parts"][0]["data"]["ap2.mandates.PaymentMandate"]

    # 서명 검증
    if verify_payment_mandate(payment_mandate):
        task["status"] = {
            "state": "completed",
            "transactionId": "tx_xxx"
        }
```

---

## Mandate 구조 (공식 스펙 기반)

### Cart Mandate

> Merchant가 생성 → User가 서명

```json
{
  "contents": {
    "id": "cart_abc123",
    "user_signature_required": true,
    "payment_request": {
      "method_data": [{"supported_methods": "CARD"}],
      "details": {
        "displayItems": [
          {"label": "Nike Air Max 90", "amount": {"currency": "USD", "value": "120"}}
        ],
        "total": {"label": "Total", "amount": {"currency": "USD", "value": "120"}}
      }
    }
  },
  "merchant_signature": "sig_xxx",
  "user_signature": "user_sig_xxx",
  "timestamp": "2026-01-25T12:00:00Z"
}
```

**포함 내용** (공식 스펙):
- Payer/Payee 정보 및 Credential Provider
- 토큰화된 결제 수단
- 리스크 신호 컨테이너
- 거래 상세: 상품, 배송지, 금액, 통화
- 환불 조건 (해당 시)
- TTL (유효 기간)

### Payment Mandate

> Agent가 생성, 결제 네트워크에 AI 관여 알림

```json
{
  "payment_mandate_contents": {
    "payment_mandate_id": "pm_xxx",
    "payment_details_id": "order_xxx"
  },
  "user_authorization": "eyJhbGciOiJFUzI1NksifQ...",
  "agent_presence_indicator": {
    "agent_initiated": true,
    "human_present": true
  }
}
```

**포함 내용** (공식 스펙):
- AI 에이전트 관여 지표
- 거래 모드 (Human Present / Human NOT Present)
- 결제 상세 ID 및 총액
- 결제 응답 데이터
- Merchant Agent 식별자
- 타임스탬프
- 사용자 인증 증명

---

## Task 상태 전이

```
┌───────────┐     tasks/create      ┌─────────────────┐
│ (없음)     │ ──────────────────▶  │ input-required  │
└───────────┘                       └────────┬────────┘
                                             │
                    message/send             │
                    (Payment Mandate)        │
                                             ▼
                                    ┌─────────────────┐
                                    │   completed     │
                                    │   (or failed)   │
                                    └─────────────────┘
```

- **input-required**: Cart Mandate 발송 후, 사용자 응답 대기
- **completed**: Payment Mandate 검증 성공, 결제 완료
- **failed**: 검증 실패 또는 오류

---

## 현재 구현의 한계 (데모용 단순화)

| 공식 스펙 | 현재 구현 |
|----------|----------|
| Cart Mandate에 User 서명 필요 | User 서명 생략 |
| 암호화 서명 검증 (ECDSA 등) | 시뮬레이션 (문자열 존재 여부만 확인) |
| Intent Mandate 지원 | 미구현 (Human Present만 지원) |

이 데모는 학습 목적으로 핵심 플로우를 이해하기 위해 단순화되었습니다.

### Intent Mandate가 필요한 시나리오

Intent Mandate는 **Human NOT Present** (사용자가 자리에 없는) 상황에서 필요합니다.

```
예시: "콘서트 티켓이 풀리면 바로 사줘"

1. User가 Intent Mandate 서명 (조건: 가격 < $200, 좌석 A구역)
2. User 자리 비움 (Human NOT Present)
3. 티켓 오픈 → Agent가 조건 확인
4. 조건 충족 시 Agent가 자동으로 Cart Mandate 생성
5. Payment Mandate 전송 → 결제 완료
```

### Intent Mandate 예시 코드 (미구현)

```python
# client_agent.py - Intent Mandate 생성 (Human NOT Present)
intent_mandate = {
    "intent_mandate_contents": {
        "intent_mandate_id": f"im_{uuid.uuid4().hex[:12]}",

        # 구매 조건
        "shopping_parameters": {
            "product_category": "concert_tickets",
            "max_price": {"currency": "USD", "value": "200.00"},
            "constraints": ["seat_section:A", "quantity:2"]
        },

        # Agent가 이해한 의도 (자연어)
        "natural_language_playback": "콘서트 티켓 2장, A구역, $200 이하로 구매"
    },

    # 사용자 서명 (사전 승인)
    "user_authorization": "eyJhbGciOiJFUzI1NksifQ...",

    # 유효 기간
    "ttl": "2026-02-01T00:00:00Z"
}
```

```python
# merchant_agent.py - Intent Mandate 처리
def handle_intent_mandate(intent_mandate):
    """
    Intent Mandate 수신 시:
    1. 조건 충족 여부 확인
    2. 충족 시 Cart Mandate 자동 생성
    3. Payment Mandate로 결제 진행
    """
    params = intent_mandate["intent_mandate_contents"]["shopping_parameters"]
    max_price = float(params["max_price"]["value"])

    # 조건에 맞는 상품 검색
    matching_products = search_products_by_constraints(params)

    if matching_products and matching_products[0]["price"] <= max_price:
        # 조건 충족 → 자동 구매 진행
        cart_mandate = create_cart_mandate(matching_products[0])
        return {"action": "proceed", "cart_mandate": cart_mandate}
    else:
        # 조건 미충족 → 대기
        return {"action": "wait"}
```

---

## 참고 자료

- [AP2 Protocol Specification](https://ap2-protocol.org/specification/)
- [Google Cloud Blog - Announcing AP2](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol)
- [An Illustrated Guide to AP2 (2025)](https://arthurchiao.art/blog/ap2-illustrated-guide/)
