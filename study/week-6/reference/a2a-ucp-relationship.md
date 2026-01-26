# A2A와 UCP의 관계 정리

## 개요

| 프로토콜 | 설명 | 발표 시점 |
|---------|------|----------|
| **A2A** (Agent-to-Agent) | 에이전트 간 통신을 위한 범용 프로토콜 | 2025년 4월 (Google) |
| **UCP** (Universal Commerce Protocol) | 에이전틱 상거래를 위한 상거래 특화 프로토콜 | 2026년 1월 11일 (NRF 2026) |

---

## 1. 프로토콜 스택에서의 위치

```
┌─────────────────────────────────────────────────────────┐
│                    Consumer Surfaces                     │
│         (Google AI Mode, Gemini, ChatGPT, Copilot)      │
├─────────────────────────────────────────────────────────┤
│                         UCP                              │
│    (상거래 기능: 검색, 장바구니, 결제, 주문관리)            │
├─────────────────────────────────────────────────────────┤
│         Transport Layer (선택 가능)                       │
│    ┌─────────┬─────────┬─────────┐                      │
│    │   A2A   │   MCP   │  REST   │                      │
│    └─────────┴─────────┴─────────┘                      │
├─────────────────────────────────────────────────────────┤
│                         AP2                              │
│              (결제 승인 및 Mandate 시스템)                 │
└─────────────────────────────────────────────────────────┘
```

**레이어별 역할:**
- **Consumer Surfaces**: 사용자 접점 (AI 어시스턴트, 검색 등)
- **UCP**: 상거래 기능 정의 (검색, 장바구니, 결제, 주문관리)
- **Transport Layer**: 통신 방식 (A2A, MCP, REST 중 선택)
- **AP2**: 결제 승인 및 신뢰 메커니즘

---

## 2. 핵심 관계

### A2A: 통신 계층 (Transport Layer)

| 항목 | 내용 |
|------|------|
| **역할** | 에이전트 간 범용 통신 프로토콜 |
| **핵심 기능** | 에이전트 발견, 메시지 교환, 태스크 관리, 아티팩트 공유 |
| **특징** | 상거래에 국한되지 않는 범용 목적 |
| **관리** | Linux Foundation (2025년 6월 이관) |

### UCP: 상거래 기능 계층 (Commerce Layer)

| 항목 | 내용 |
|------|------|
| **역할** | 상거래 여정 전체를 위한 기능 정의 |
| **핵심 기능** | 상품 검색, 장바구니 관리, 결제, 주문 후 관리 |
| **특징** | A2A/MCP/REST를 전송 메커니즘으로 활용 |
| **개발** | Google + Shopify, Etsy, Wayfair, Target, Walmart |

---

## 3. 상호 보완적 역할

| 측면 | A2A | UCP |
|------|-----|-----|
| **범위** | 범용 에이전트 통신 | 상거래 특화 |
| **추상화 수준** | 낮음 (메시징 프리미티브) | 높음 (비즈니스 로직) |
| **독립성** | 상거래 외 용도로도 사용 | A2A/MCP/REST 위에서 동작 |
| **데이터 타입** | 범용 메시지/아티팩트 | 상거래 특화 (Product, Cart, Order) |
| **관계** | 전송 계층 제공 | A2A를 전송 옵션으로 활용 |

### 비유로 이해하기

```
A2A  = 도로 (어디든 갈 수 있는 인프라)
UCP  = 택배 시스템 (도로 위에서 동작하는 상거래 서비스)
AP2  = 결제 단말기 (거래 승인 처리)
```

---

## 4. 기술적 통합 방식

### 4.1 A2A Agent Card에서 UCP 확장 선언

```json
{
  "protocolVersion": "0.3.0",
  "name": "E-Commerce Merchant Agent",
  "url": "https://merchant.example.com/a2a/v1",
  "extensions": [
    {
      "uri": "https://ucp.dev/extensions/commerce/v1",
      "description": "UCP Commerce Extension"
    },
    {
      "uri": "https://google-a2a.github.io/A2A/extensions/payments/v1",
      "description": "AP2 Payment Extension"
    }
  ],
  "skills": [
    {
      "id": "product-search",
      "name": "상품 검색",
      "tags": ["ucp", "discovery"]
    },
    {
      "id": "checkout",
      "name": "결제 처리",
      "tags": ["ucp", "checkout", "ap2"]
    }
  ]
}
```

### 4.2 UCP의 전송 방식 옵션

UCP는 세 가지 전송 방식을 지원합니다:

| 전송 방식 | 설명 | 적합한 경우 |
|----------|------|------------|
| **A2A** | 에이전트 간 직접 통신 | 복잡한 에이전트 협업 시나리오 |
| **MCP** | 모델-도구 연결 | LLM이 직접 상거래 도구 호출 |
| **REST** | 전통적 API 호출 | 기존 시스템 통합, 단순 연동 |

### 4.3 A2A Binding for UCP

A2A를 통해 UCP 기능을 사용하는 예시:

```json
// A2A 메시지로 UCP ProductSearch 요청
{
  "messageId": "msg-001",
  "role": "user",
  "parts": [
    {
      "kind": "data",
      "data": {
        "ucp.discovery.ProductSearchRequest": {
          "query": "빨간색 나이키 운동화",
          "filters": {
            "price_max": 150,
            "currency": "USD"
          },
          "page_size": 10
        }
      }
    }
  ]
}
```

```json
// A2A 메시지로 UCP ProductSearch 응답
{
  "messageId": "msg-002",
  "role": "agent",
  "parts": [
    {
      "kind": "data",
      "data": {
        "ucp.discovery.ProductSearchResponse": {
          "products": [
            {
              "id": "nike-airmax-90-red",
              "title": "Nike Air Max 90 (Red)",
              "price": { "currency": "USD", "value": 120 },
              "availability": "IN_STOCK"
            }
          ],
          "total_results": 42
        }
      }
    }
  ]
}
```

---

## 5. 실제 구현 흐름

```
[사용자] "빨간 운동화 찾아서 제일 싼 거 사줘"
    │
    ▼
[쇼핑 에이전트]
    │
    │ (1) A2A: Agent Discovery
    ▼
[판매자 에이전트 A] ←──────────────────┐
[판매자 에이전트 B] ←──────────────────┤ A2A 통신
[판매자 에이전트 C] ←──────────────────┘
    │
    │ (2) UCP: ProductSearch (A2A 위에서)
    ▼
[검색 결과 수집 및 비교]
    │
    │ (3) UCP: CreateCart + Checkout
    ▼
[최저가 판매자 선택]
    │
    │ (4) AP2: Payment Mandate
    ▼
[결제 처리]
    │
    │ (5) UCP: OrderConfirmation
    ▼
[사용자에게 결과 전달]
```

---

## 6. UCP 핵심 기능 (Capabilities)

UCP가 정의하는 상거래 기능들:

### 6.1 Discovery (상품 검색)

```
ProductSearch      - 상품 검색
ProductDetails     - 상품 상세 정보
InventoryCheck     - 재고 확인
```

### 6.2 Cart Management (장바구니)

```
CreateCart         - 장바구니 생성
AddToCart          - 상품 추가
UpdateCart         - 수량 변경
RemoveFromCart     - 상품 제거
```

### 6.3 Checkout (결제)

```
InitiateCheckout   - 결제 시작
ApplyPromotion     - 프로모션 적용
CalculateShipping  - 배송비 계산
SubmitOrder        - 주문 제출
```

### 6.4 Post-Purchase (주문 후)

```
OrderStatus        - 주문 상태 조회
TrackShipment      - 배송 추적
RequestReturn      - 반품 요청
CustomerSupport    - 고객 지원
```

---

## 7. 주요 파트너 및 생태계

### UCP 공동 개발사

| 카테고리 | 기업 |
|---------|------|
| **플랫폼** | Google |
| **커머스** | Shopify, Etsy, Wayfair, Target, Walmart |

### UCP 지원사 (60+ 조직)

| 카테고리 | 기업 |
|---------|------|
| **결제** | Adyen, Mastercard, PayPal, Stripe, Visa |
| **리테일** | Best Buy, Flipkart, Macy's, The Home Depot, Zalando |
| **기술** | American Express, Google, Microsoft |

---

## 8. FAQ

### Q1: UCP가 A2A를 대체하나요?

**아니오.** UCP는 A2A를 대체하지 않습니다. UCP는 A2A 위에서 동작하는 상거래 특화 레이어입니다. A2A는 범용 에이전트 통신을 담당하고, UCP는 그 위에서 상거래 기능을 정의합니다.

### Q2: A2A 없이 UCP를 사용할 수 있나요?

**예.** UCP는 A2A 외에도 MCP나 REST API를 통해 사용할 수 있습니다. 전송 방식은 비즈니스 요구사항에 따라 선택합니다.

### Q3: AP2와 UCP의 관계는?

**상호 보완적입니다.** UCP는 상거래 여정(검색→결제→주문관리)을 정의하고, AP2는 그 중 결제 승인 부분의 신뢰 메커니즘(Mandate 시스템)을 담당합니다.

### Q4: ACP (OpenAI/Stripe)와 UCP의 관계는?

둘 다 에이전틱 상거래 표준이지만 접근 방식이 다릅니다:
- **ACP**: OpenAI/Stripe 중심, ChatGPT Instant Checkout에 최적화
- **UCP**: Google 중심, 더 넓은 상거래 여정 커버 (검색부터 주문 후까지)

향후 상호 운용성 확보를 위한 협력이 예상됩니다.

---

## 9. 참고 자료

### 공식 문서
- [UCP 공식 문서](https://ucp.dev/specification/overview/)
- [UCP A2A Binding 스펙](https://ucp.dev/specification/checkout-a2a/)
- [A2A Protocol 공식](https://a2a-protocol.org/latest/)

### 블로그 및 발표
- [Google Developers Blog - UCP](https://developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp/)
- [Google for Developers - UCP Guide](https://developers.google.com/merchant/ucp)

### GitHub
- [UCP GitHub](https://github.com/Universal-Commerce-Protocol/ucp)
- [A2A GitHub](https://github.com/a2aproject/A2A)

---

*작성일: 2026-01-25*
*Week 6 보충 자료 - A2A와 UCP 관계*
