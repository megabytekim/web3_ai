# 2. What: 프로토콜 스택

> **발표 시간**: 25분

---

## 전체 구조 (5분)

### 프로토콜 스택 다이어그램

```
┌─────────────────────────────────────────────────────────┐
│              AI Agent (Claude, Gemini, ChatGPT)         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│    ┌─────────────┐              ┌─────────────┐        │
│    │     MCP     │              │     A2A     │        │
│    │  (도구 연결) │              │ (에이전트 통신)│        │
│    └─────────────┘              └─────────────┘        │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                         UCP                             │
│           (상거래 기능: 검색 → 결제 → 주문관리)            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│    ┌─────────────┐              ┌─────────────┐        │
│    │     AP2     │              │    x402     │        │
│    │ (결제 승인)  │              │   (정산)    │        │
│    └─────────────┘              └─────────────┘        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 비유로 이해하기

| 프로토콜 | 비유 | 역할 |
|---------|------|------|
| **MCP** | 만능 리모컨 | AI가 외부 도구 사용 |
| **A2A** | 도로 | 에이전트끼리 대화 |
| **UCP** | 택배 시스템 | 상거래 흐름 정의 |
| **AP2** | 결제 단말기 | 결제 승인 |
| **x402** | 자판기 동전 투입구 | 즉시 정산 |

---

## A2A + AP2 (8분)

### A2A (Agent-to-Agent Protocol)

**발표**: Google, 2025년 4월 → Linux Foundation 이관 (2025년 6월)

**핵심 개념**:
- **Agent Card**: `/.well-known/agent.json`에서 에이전트 발견
- **JSON-RPC**: 에이전트 간 메시지 교환
- **Task**: 세션 개념, 여러 메시지 주고받음

```json
// Agent Card 예시
{
  "name": "Flower Shop Agent",
  "url": "https://flowers.example.com/a2a",
  "skills": ["product-search", "checkout"]
}
```

### AP2 (Agent Payments Protocol)

**발표**: Google, 2025년 9월 (60개+ 파트너)

**핵심: Mandate 시스템**

| Mandate 종류 | 용도 | 서명 |
|-------------|------|------|
| **Cart Mandate** | Human-Present (사용자 확인 후 결제) | 판매자 + 사용자 |
| **Intent Mandate** | Human-Not-Present (자동 구매) | 사용자 사전 서명 |
| **Payment Mandate** | 결제 네트워크 전송용 | 에이전트 |

**Human-Present vs Human-Not-Present**

```
[Human-Present]
사용자: "꽃 찾아줘" → 에이전트: "이거 어때요?" → 사용자: "OK 사줘" → 결제

[Human-Not-Present]
사용자: "콘서트 티켓 120달러 이하면 자동으로 사" → (에이전트가 조건 충족 시 자동 구매)
```

---

## UCP (8분)

### Universal Commerce Protocol

**발표**: Google, NRF 2026 (2026년 1월)
**파트너**: Shopify, Etsy, Wayfair, Target, Walmart, Visa, Mastercard 등 60개+

### 핵심 개념

**1. Capability Profile**
```json
// /.well-known/ucp.json
{
  "merchant_name": "Demo Shop",
  "capabilities": {
    "discovery": { "product_search": true },
    "checkout": { "create_session": true }
  }
}
```

**2. 상거래 전체 여정 커버**

```
검색 (Discovery)
    │
    ▼
장바구니 (Cart)
    │
    ▼
결제 (Checkout)
    │
    ▼
주문관리 (Post-Purchase)
```

**3. Transport 선택 가능**

| Transport | 적합한 경우 |
|-----------|------------|
| **A2A** | 복잡한 에이전트 협업 |
| **MCP** | LLM이 직접 도구 호출 |
| **REST** | 기존 시스템 통합 |

### A2A vs UCP 관계

> UCP는 A2A를 **대체하지 않음**. A2A 위에서 동작하는 **상거래 레이어**.

---

## x402 (5분)

### HTTP 402 기반 결제 프로토콜

**발표**: Coinbase, 2025년 5월
**파트너**: Cloudflare, Visa, Anthropic

### 핵심: Stateless (무상태)

> **"자판기처럼 작동"** - 동전 넣으면 바로 음료 나옴

| 특성 | 설명 |
|------|------|
| **세션 없음** | 매 요청이 독립적 |
| **즉시 정산** | 2초 미만 |
| **수수료 제로** | 프로토콜 수수료 없음 |

### 작동 방식

```
[Client]                              [Server]
    │                                     │
    │ GET /api/premium-data               │
    │ ───────────────────────────────────>│
    │                                     │
    │         402 Payment Required        │
    │         (결제 조건 포함)              │
    │ <───────────────────────────────────│
    │                                     │
    │ GET /api/premium-data               │
    │ X-PAYMENT: <base64 encoded>         │
    │ ───────────────────────────────────>│
    │                                     │
    │         200 OK + Data               │
    │ <───────────────────────────────────│
```

### X-PAYMENT 헤더 구조

```json
{
  "version": 1,
  "from": "0xClient...",
  "to": "0xServer...",
  "amount": "100000",
  "asset": "USDC",
  "chain": "base",
  "nonce": "replay-방지-값",
  "signature": "0x..."
}
```

### Stateless의 장단점

| 장점 | 단점 |
|------|------|
| 단순함 | 장바구니 불가 |
| 확장성 | 환불 복잡 |
| 캐싱 가능 | 구독 불가 |

---

## 3종 비교표 (2분)

| | A2A + AP2 | UCP | x402 |
|---|-----------|-----|------|
| **주도** | Google | Google | Coinbase |
| **복잡도** | 높음 | 중간 | **낮음** |
| **통신** | JSON-RPC | REST/A2A/MCP | HTTP 상태코드 |
| **결제** | Mandate 시스템 | Checkout Session | X-PAYMENT 헤더 |
| **정산** | 기존 결제망 | 기존 결제망 | **온체인 (2초)** |
| **적합 용도** | 복잡한 협업 거래 | 범용 상거래 | **마이크로페이먼트** |
| **환불** | 가능 | 가능 | 어려움 |
| **장바구니** | 가능 | 가능 | 불가 |

### 언제 무엇을 쓸까?

- **"복잡한 B2C 쇼핑"** → A2A + AP2 + UCP
- **"기존 쇼핑몰에 AI 연동"** → UCP (REST)
- **"API 호출당 과금"** → x402
- **"AI 서비스 간 정산"** → x402

---

*참조: [reference/theory-ap2.md](../reference/theory-ap2.md), [reference/a2a-ucp-relationship.md](../reference/a2a-ucp-relationship.md)*
