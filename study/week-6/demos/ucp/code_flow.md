# UCP 코드 플로우

## UCP 공식 스펙 요약

> **출처**: [UCP Specification](https://ucp.dev/specification/overview/)

UCP(Universal Commerce Protocol)는 2026년 1월 Google이 NRF Retail's Big Show에서 발표한 **에이전틱 커머스를 위한 오픈 표준**입니다.

### 주요 파트너

- **플랫폼**: Shopify, Etsy, Wayfair
- **리테일러**: Target, Walmart, Best Buy, Macy's, The Home Depot
- **결제**: Visa, Mastercard, American Express, Stripe, Adyen

### 핵심 설계 원칙

| 원칙 | 설명 |
|------|------|
| **Composable Architecture** | Capability 단위로 기능 구성 (Checkout, Discovery 등) |
| **Dynamic Discovery** | `/.well-known/ucp.json`에서 지원 기능 자동 발견 |
| **Transport Agnostic** | REST, MCP, A2A 등 다양한 전송 방식 지원 |
| **Decoupled Payments** | 결제 수단(Instrument)과 처리기(Handler) 분리 |

---

## A2A vs UCP 비교

| 구분 | A2A + AP2 | UCP |
|------|-----------|-----|
| **발견** | Agent Card | Capability Profile |
| **통신** | JSON-RPC | REST API (기본) |
| **결제** | Mandate 시스템 | Checkout Session |
| **초점** | AI 에이전트 간 통신 | 범용 상거래 표준 |
| **확장** | Extensions | Capabilities + Extensions |

```
A2A + AP2: 에이전트 ↔ 에이전트 (P2P)
UCP: 에이전트 ↔ 비즈니스 (B2C/B2B)
```

---

## 핵심 개념

### Capability Profile

비즈니스가 지원하는 UCP 기능을 선언하는 문서입니다.

```
/.well-known/ucp.json
├── merchant: 상점 정보
├── capabilities
│   ├── discovery: 상품 검색/조회
│   ├── checkout: 결제 세션/주문
│   └── payment_methods: 지원 결제 수단
└── transports: REST, MCP, A2A
```

### Checkout Session

UCP의 결제는 **세션 기반**입니다. A2A의 Task와 유사하게 상태를 추적합니다.

```
Session (session_abc123)
├── 상태: pending → completed
├── items: 장바구니 아이템
├── subtotal: 상품 금액
├── shipping: 배송 옵션/비용
└── total: 총액
```

---

## 전체 플로우

```
┌─────────────────┐                    ┌─────────────────┐
│  Shopping Agent │                    │   Merchant      │
│   (클라이언트)    │                    │    (서버)       │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
    [1]  │  GET /.well-known/ucp.json           │
         │ ────────────────────────────────────▶│
         │                                      │
         │  Capability Profile                  │
         │ ◀────────────────────────────────────│
         │  (discovery, checkout 지원 여부)      │
         │                                      │
    [2]  │  POST /ucp/discovery/search          │
         │  {"query": "rose"}                   │
         │ ────────────────────────────────────▶│
         │                                      │
         │  검색 결과                            │
         │ ◀────────────────────────────────────│
         │  [{title: "Red Rose", price: $45}]   │
         │                                      │
    [3]  │  POST /ucp/checkout/session          │
         │  {cart: {items: [...]}}              │
         │ ────────────────────────────────────▶│
         │                                      │
         │  Checkout Session                    │
         │ ◀────────────────────────────────────│
         │  {session_id, total: $50}            │
         │                                      │
    [4]  │  POST /ucp/checkout/submit           │
         │  {session_id, payment, address}      │
         │ ────────────────────────────────────▶│
         │                                      │
         │  Order Confirmation                  │
         │ ◀────────────────────────────────────│
         │  {order_id, status: confirmed}       │
         │                                      │
```

---

## 코드 매핑

### Step 1: Capability 발견

**client_demo.py**
```python
def discover_capabilities(self) -> dict:
    response = self.http.get(f"{MERCHANT_URL}/.well-known/ucp.json")
    return response.json()

# 사용
capabilities = self.discover_capabilities()
caps = capabilities.get("capabilities", {})

# Discovery 지원 여부 확인
discovery_enabled = caps.get("discovery", {}).get("product_search", {}).get("enabled", False)
```

**merchant_server.py** (36-99줄)
```python
@app.route("/.well-known/ucp.json", methods=["GET"])
def capability_profile():
    return jsonify({
        "version": "1.0",
        "merchant": {
            "name": "Demo Flower Shop",
            "url": "http://localhost:5002"
        },
        "capabilities": {
            "discovery": {
                "product_search": {"enabled": True, "endpoint": "/ucp/discovery/search"}
            },
            "checkout": {
                "create_session": {"enabled": True, "endpoint": "/ucp/checkout/session"}
            }
        },
        "transports": {"rest": {"base_url": "http://localhost:5002"}}
    })
```

### Step 2: 상품 검색 (Discovery)

**client_demo.py**
```python
def search_products(self, query: str) -> dict:
    response = self.http.post(
        f"{MERCHANT_URL}/ucp/discovery/search",
        json={"query": query, "page_size": 10}
    )
    return response.json()

# 사용
result = self.search_products("rose")
products = result["data"]["products"]
# [{"id": "flower-001", "title": "Red Rose Bouquet", "price": {"value": "45.00"}}]
```

**merchant_server.py** (106-144줄)
```python
@app.route("/ucp/discovery/search", methods=["POST"])
def product_search():
    data = request.json or {}
    query = data.get("query", "").lower()

    # 검색 로직
    results = [p for p in PRODUCTS if query in p["title"].lower()]

    return jsonify({
        "success": True,
        "data": {
            "products": results,
            "total_results": len(results)
        }
    })
```

### Step 3: 결제 세션 생성 (Checkout)

**client_demo.py**
```python
def create_checkout_session(self, product_id: str) -> dict:
    response = self.http.post(
        f"{MERCHANT_URL}/ucp/checkout/session",
        json={
            "cart": {"items": [{"product_id": product_id, "quantity": 1}]},
            "shipping_option": "standard"
        }
    )
    return response.json()

# 응답
# {
#   "session_id": "session_abc123",
#   "status": "pending",
#   "subtotal": {"currency": "USD", "value": "45.00"},
#   "shipping": {"cost": {"value": "5.00"}},
#   "total": {"currency": "USD", "value": "50.00"}
# }
```

**merchant_server.py** (167-246줄)
```python
@app.route("/ucp/checkout/session", methods=["POST"])
def create_checkout_session():
    data = request.json or {}
    cart = data.get("cart", {})

    # 장바구니 계산
    items = []
    subtotal = 0.0
    for cart_item in cart.get("items", []):
        product = find_product(cart_item["product_id"])
        subtotal += float(product["price"]["value"])
        items.append(...)

    # 배송비
    shipping_cost = 5.00  # standard

    # 세션 생성
    session = {
        "session_id": f"session_{uuid.uuid4().hex[:12]}",
        "status": "pending",
        "items": items,
        "subtotal": {"currency": "USD", "value": f"{subtotal:.2f}"},
        "total": {"currency": "USD", "value": f"{subtotal + shipping_cost:.2f}"}
    }

    CHECKOUT_SESSIONS[session["session_id"]] = session
    return jsonify({"success": True, "data": session})
```

### Step 4: 주문 제출

**client_demo.py**
```python
def submit_order(self, session_id: str, payment: dict, shipping_address: dict) -> dict:
    response = self.http.post(
        f"{MERCHANT_URL}/ucp/checkout/submit",
        json={
            "session_id": session_id,
            "payment": {"method": "CARD", "token": "tok_visa_xxx"},
            "shipping_address": {...}
        }
    )
    return response.json()

# 응답
# {
#   "order_id": "order_xyz789",
#   "status": "confirmed",
#   "payment": {"status": "paid", "transaction_id": "tx_xxx"}
# }
```

**merchant_server.py** (249-319줄)
```python
@app.route("/ucp/checkout/submit", methods=["POST"])
def submit_order():
    session_id = data.get("session_id")
    session = CHECKOUT_SESSIONS.get(session_id)

    if session["status"] != "pending":
        return error("Session already processed")

    # 주문 생성
    order = {
        "order_id": f"order_{uuid.uuid4().hex[:12]}",
        "status": "confirmed",
        "items": session["items"],
        "total": session["total"],
        "payment": {
            "method": payment.get("method"),
            "status": "paid",
            "transaction_id": f"tx_{uuid.uuid4().hex[:12]}"
        }
    }

    session["status"] = "completed"
    return jsonify({"success": True, "data": {"order": order}})
```

---

## Capability Profile 구조

```json
{
  "version": "1.0",
  "merchant": {
    "name": "Demo Flower Shop",
    "description": "UCP 데모용 꽃집",
    "url": "http://localhost:5002"
  },
  "capabilities": {
    "discovery": {
      "product_search": {
        "enabled": true,
        "endpoint": "/ucp/discovery/search",
        "method": "POST"
      },
      "product_details": {
        "enabled": true,
        "endpoint": "/ucp/discovery/product/{product_id}",
        "method": "GET"
      }
    },
    "checkout": {
      "create_session": {
        "enabled": true,
        "endpoint": "/ucp/checkout/session",
        "method": "POST"
      },
      "submit_order": {
        "enabled": true,
        "endpoint": "/ucp/checkout/submit",
        "method": "POST"
      }
    },
    "payment_methods": ["CARD", "PAYPAL"],
    "shipping_options": [
      {"id": "standard", "label": "표준 배송", "price": "5.00"},
      {"id": "express", "label": "빠른 배송", "price": "15.00"}
    ]
  },
  "transports": {
    "rest": {"base_url": "http://localhost:5002"}
  }
}
```

---

## Checkout Session 상태 전이

```
┌───────────┐    create_session     ┌───────────┐
│ (없음)     │ ────────────────────▶ │  pending  │
└───────────┘                       └─────┬─────┘
                                          │
                    submit_order          │
                                          ▼
                                    ┌───────────┐
                                    │ completed │
                                    └───────────┘
```

- **pending**: 세션 생성됨, 결제 대기 중
- **completed**: 주문 제출 완료

---

## 현재 구현의 한계 (데모용 단순화)

| 공식 스펙 | 현재 구현 |
|----------|----------|
| 다양한 Transport (REST, MCP, A2A) | REST만 구현 |
| Payment Handler 분리 | 직접 처리 (시뮬레이션) |
| Tokenized Payments | 토큰 검증 없음 |
| Extensions 시스템 | 미구현 |

이 데모는 학습 목적으로 핵심 플로우를 이해하기 위해 단순화되었습니다.

---

## UCP vs A2A vs AP2 관계

### 프로토콜 계층 구조

```
┌─────────────────────────────────────────────────────┐
│                    UCP (상거래)                      │
│         "무엇을 살 수 있고, 어떻게 사는지"             │
├─────────────────────────────────────────────────────┤
│                                                     │
│    ┌─────────────┐         ┌─────────────┐         │
│    │     A2A     │         │    REST     │   ...   │
│    │ (에이전트간) │         │   (일반)    │         │
│    └──────┬──────┘         └─────────────┘         │
│           │                                         │
│    ┌──────┴──────┐                                 │
│    │     AP2     │                                 │
│    │  (결제 확장) │                                 │
│    └─────────────┘                                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 핵심 차이

| | A2A | AP2 | UCP |
|---|-----|-----|-----|
| **역할** | 통신 프로토콜 | 결제 확장 | 상거래 표준 |
| **범위** | 에이전트 ↔ 에이전트 | A2A 위에서 결제 | 비즈니스 ↔ 에이전트 |
| **관계** | 기반 프로토콜 | A2A의 Extension | **독립적** (A2A를 transport로 사용 가능) |

### 비유로 설명

```
A2A  = 전화기 (통화 방법)
AP2  = 전화로 송금하는 규칙 (A2A 위에서만 동작)
UCP  = 쇼핑몰 표준 (전화, 웹, 앱 등 다양한 방식으로 접근 가능)
```

### 실제 조합

UCP는 transport를 선택할 수 있습니다:

```json
{
  "transports": {
    "rest": {"base_url": "..."},
    "mcp": {"server": "..."},
    "a2a": {"agent_url": "..."}
  }
}
```

- **REST**: 일반 HTTP API로 접근
- **MCP**: Model Context Protocol로 접근
- **A2A**: Agent-to-Agent 프로토콜로 접근 (이 경우 AP2도 사용 가능)

### 정리

- **A2A + AP2**: 에이전트끼리 대화하고 결제하는 방법
- **UCP**: 상점이 "나는 이런 기능을 제공해요"라고 선언하는 표준 (A2A든 REST든 상관없이)

---

## 참고 자료

- [UCP Official Documentation](https://ucp.dev/)
- [UCP Specification Overview](https://ucp.dev/specification/overview/)
- [GitHub - Universal-Commerce-Protocol/ucp](https://github.com/Universal-Commerce-Protocol/ucp)
- [Google Developers Blog - Under the Hood: UCP](https://developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp/)
