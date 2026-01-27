# 2. What: 프로토콜 스택

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

### 프로토콜 요약

**MCP (Model Context Protocol)**
- Anthropic이 제안한 AI-도구 연결 표준
- LLM이 DB, API, 파일시스템 등 외부 리소스에 접근할 수 있게 해줌
- 현재 Claude, Cursor, VS Code 등 주요 AI 도구에서 채택

**A2A (Agent-to-Agent Protocol)**
- Google이 제안한 에이전트 간 통신 규격
- Agent Card(`/.well-known/agent.json`)로 서로 발견하고 JSON-RPC로 메시지 교환
- 2025년 6월 Linux Foundation에 이관되어 오픈 표준으로 발전 중

**UCP (Universal Commerce Protocol)**
- 상거래 전체 여정(검색→장바구니→결제→주문관리)을 정의
- A2A/MCP/REST 등 다양한 Transport 위에서 동작 가능
- Shopify, Walmart, Visa 등 60개+ 파트너가 참여

**AP2 (Agent Payments Protocol)**
- 에이전트 결제 승인 프로토콜
- Mandate(위임장) 시스템으로 사용자 동의 관리
- Human-Present(확인 후 결제) / Human-Not-Present(조건부 자동 결제) 모두 지원

**x402 (HTTP 402 Protocol)**
- Coinbase가 제안한 즉시 결제 프로토콜
- HTTP 402 상태코드 + X-PAYMENT 헤더로 결제 처리
- 지원 체인: **Base**(Coinbase L2), **Solana** / 결제 수단: **USDC**
- 수수료 제로, $0.001 수준 마이크로페이먼트 가능
- 파트너: Cloudflare(x402 Foundation 공동 설립), Google(AP2에 통합)

> **용어 설명**
> - **Base**: Coinbase가 만든 이더리움 L2(레이어2) 블록체인. 이더리움보다 훨씬 빠르고(2초 미만) 수수료가 저렴
> - **Solana**: 초당 수천 건 처리 가능한 고속 블록체인. 트랜잭션 비용이 $0.001 미만
> - **USDC**: Circle사가 발행하는 달러 연동 스테이블코인(1 USDC = 1 USD). Coinbase가 공동 설립

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

| Mandate 종류 | 역할 | 서명 |
|-------------|------|------|
| **Intent Mandate** | 요청 맥락 기록 (검색 조건, 사전 승인 조건) | 사용자 |
| **Cart Mandate** | 구매 확정 기록 (정확한 상품/가격) | 판매자 + 사용자 |
| **Payment Mandate** | 결제 실행 기록 | 에이전트 |

**Human-Present vs Human-Not-Present**

- **Human-Present**: 사용자가 실시간으로 각 단계 승인
- **Human-Not-Present**: 사용자가 사전에 조건 설정, 조건 충족 시 자동 진행

```
[Human-Present]
사용자: "꽃 찾아줘" → 에이전트: "이거 어때요?" → 사용자: "OK 사줘" → 결제

[Human-Not-Present]
사용자: "콘서트 티켓 120달러 이하면 자동으로 사" → (에이전트가 조건 충족 시 자동 구매)
```

**Mandate란?**
- 라틴어 "mandatum"(명령, 위임)에서 유래
- AP2에서는 **암호화 서명된 디지털 위임장**을 의미
- 사용자가 에이전트에게 결제 권한을 위임했다는 변조 불가능한 증거
- 분쟁 발생 시 "누가 무엇을 승인했는가"를 증명

**Mandate 체인: 배타적이 아닌 순차적**

Cart와 Intent는 서로 배타적이 아니라, 거래 단계별로 함께 사용됨:

```
Intent Mandate → Cart Mandate → Payment Mandate
 (요청 맥락)      (상품/가격)      (결제 실행)
```

| 단계 | Mandate | 기록 내용 |
|------|---------|----------|
| 1 | Intent | "무엇을 요청했는가" (검색 조건, 사전 승인 조건) |
| 2 | Cart | "무엇을 구매하기로 했는가" (정확한 상품, 가격) |
| 3 | Payment | "어떻게 결제했는가" (결제 수단, 금액) |

이 체인이 완전한 감사 추적(Audit Trail)을 형성하여 거래의 투명성 보장

---

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

## x402

### HTTP 402 기반 결제 프로토콜

**발표**: Coinbase, 2025년 5월
**파트너**: Cloudflare, Visa, Anthropic

### 핵심: Stateless (무상태)

> **"자판기처럼 작동"** - 동전 넣으면 바로 음료 나옴

| 특성 | 설명 |
|------|------|
| **세션 없음** | 매 요청이 독립적 |
| **즉시 정산** | 2초 미만 |
| **수수료** | 프로토콜 수수료 없음 (가스비만 ~$0.001) |

> **왜 수수료가 없나?**
> - 마이크로페이먼트($0.001~$0.01)가 목표
> - 기존 결제: 고정비($0.30~$0.49)가 있어 소액 결제 불가능
> - x402: 프로토콜 수수료 없이 가스비만 → $0.01 결제도 가능
> - Coinbase는 USDC 생태계 확장으로 수익 창출

**결제 수단별 수수료 비교**

| 결제 수단 | 수수료 |
|----------|--------|
| Visa/Mastercard | 1.15%~2.90% + $0.05~$0.10 |
| Stripe | 2.9% + $0.30 |
| PayPal | 2.59%~3.49% + $0.49 |
| PayPal 소액결제 | 5% + $0.05 |
| **x402** | **가스비만 ~$0.001** |

**$0.10 결제 시 실제 수수료:**
- Stripe: $0.30 → **300%** (결제금액보다 수수료가 큼)
- PayPal 소액: $0.055 → **55%**
- x402: ~$0.001 → **1%**

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

## 3종 비교표

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
