# AP2 Protocol Architecture

## 아키텍처 개요

AP2는 A2A 프로토콜 위에 구축된 확장(Extension)으로, 에이전트 간 안전한 결제를 가능하게 합니다.

```
┌─────────────────────────────────────────────────────┐
│              User (사용자)                           │
│              - 최종 권한 보유                         │
│              - 의도 확인 및 승인                      │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│         Shopping Agent (Shopper Role)               │
│         - A2A로 에이전트 통신                        │
│         - MCP로 데이터 접근                          │
│         - AP2로 결제 협상                            │
└─────────┬───────────────────────┬───────────────────┘
          │                       │
┌─────────▼──────────┐  ┌────────▼─────────────┐
│  Merchant Agent    │  │ Credentials Provider │
│  - 카탈로그 제공    │  │ - 결제 방법 관리      │
│  - CartMandate 생성│  │ - OAuth2 인증        │
│  - 주문 처리       │  │ - 배송 주소 제공      │
└────────┬───────────┘  └──────────────────────┘
         │
┌────────▼─────────────┐
│  Payment Processor   │
│  - 결제 승인          │
│  - 거래 검증          │
│  - 완료 확인          │
└──────────────────────┘
```

## 4가지 에이전트 역할

### 1. Shopping Agent (Shopper)

사용자를 대신하여 쇼핑하는 에이전트:

**책임**:
- 제품 검색 및 비교
- 판매자 에이전트와 통신
- 장바구니 관리
- 결제 방법 선택
- CartMandate 검증
- 거래 완료

**Agent Card 예제**:
```json
{
  "name": "ShoppingAgent",
  "description": "A user's shopping assistant agent.",
  "capabilities": {
    "extensions": [
      {
        "description": "Supports AP2 payments",
        "required": true,
        "uri": "https://google-a2a.github.io/A2A/ext/payments/v1",
        "params": {
          "roles": ["shopper"]
        }
      }
    ]
  },
  "skills": [
    {
      "id": "search_products",
      "name": "Search Products",
      "description": "Search for products across merchants"
    },
    {
      "id": "compare_prices",
      "name": "Compare Prices",
      "description": "Compare prices across different merchants"
    }
  ],
  "url": "http://example.com/shopping_agent"
}
```

### 2. Merchant Agent

판매자를 대표하는 에이전트:

**책임**:
- 제품 카탈로그 제공
- 가격 및 재고 정보 제공
- 결제 방법 선언
- CartMandate 생성 및 서명
- 주문 처리

**Agent Card 예제**:
```json
{
  "name": "MerchantAgent",
  "description": "A sales assistant agent for a merchant.",
  "capabilities": {
    "extensions": [
      {
        "description": "Supports AP2 payments",
        "required": true,
        "uri": "https://google-a2a.github.io/A2A/ext/payments/v1",
        "params": {
          "roles": ["merchant"]
        }
      },
      {
        "description": "Supports Visa payment method",
        "required": true,
        "uri": "https://visa.github.io/paymentmethod/types/v1"
      }
    ]
  },
  "skills": [
    {
      "id": "search_catalog",
      "name": "Search Catalog",
      "description": "Finds items in the merchant's catalog",
      "tags": ["merchant", "search", "catalog"]
    }
  ],
  "url": "http://example.com/a2a/merchant_agent"
}
```

### 3. Credentials Provider

사용자의 결제 정보를 안전하게 관리하는 에이전트:

**책임**:
- 결제 방법 저장 및 관리
- 배송 주소 제공
- OAuth2 인증
- 안전한 자격증명 처리

**Agent Card 예제**:
```json
{
  "name": "CredentialProvider",
  "description": "An agent that holds a user's payment credentials.",
  "capabilities": {
    "extensions": [
      {
        "description": "Supports AP2 payments",
        "required": true,
        "uri": "https://google-a2a.github.io/A2A/ext/payments/v1",
        "params": {
          "roles": ["credentials-provider"]
        }
      }
    ]
  },
  "security": [
    {
      "oauth2": ["get_payment_methods"]
    }
  ],
  "securitySchemes": {
    "oauth2": {
      "flows": {
        "authorizationCode": {
          "authorizationUrl": "http://example.com/auth",
          "scopes": {
            "get_payment_methods": "Access payment methods"
          },
          "tokenUrl": "http://example.com/token"
        }
      },
      "type": "oauth2"
    }
  },
  "skills": [
    {
      "id": "get_eligible_payment_methods",
      "name": "Get Eligible Payment Methods",
      "description": "Provides a list of payment methods for a purchase"
    },
    {
      "id": "get_account_shipping_address",
      "name": "Get Shipping Address",
      "description": "Fetches the shipping address"
    }
  ],
  "url": "http://example.com/a2a/credential_provider"
}
```

### 4. Payment Processor

실제 결제를 처리하는 에이전트:

**책임**:
- 결제 승인 처리
- 거래 검증
- 3D Secure 등 추가 인증
- 결제 완료 확인

## 핵심 데이터 구조

### CartMandate

장바구니와 결제 요청의 증명:

```json
{
  "contents": {
    "id": "cart_shoes_123",
    "user_signature_required": false,
    "payment_request": {
      "method_data": [
        {
          "supported_methods": "CARD",
          "data": {
            "payment_processor_url": "http://example.com/pay"
          }
        }
      ],
      "details": {
        "id": "order_shoes_123",
        "displayItems": [
          {
            "label": "Cool Shoes Max",
            "amount": {
              "currency": "USD",
              "value": 120.0
            }
          }
        ],
        "shipping_options": null,
        "modifiers": null,
        "total": {
          "label": "Total",
          "amount": {
            "currency": "USD",
            "value": 120.0
          }
        }
      },
      "options": {
        "requestPayerName": false,
        "requestPayerEmail": false,
        "requestPayerPhone": false,
        "requestShipping": true
      }
    }
  },
  "merchant_signature": "sig_merchant_shoes_abc1",
  "timestamp": "2025-08-26T19:36:36.377022Z"
}
```

**주요 필드**:
- `id`: 장바구니 고유 ID
- `user_signature_required`: 사용자 서명 필요 여부
- `payment_request`: 결제 요청 상세
  - `method_data`: 지원하는 결제 방법
  - `details`: 주문 상세 (항목, 금액)
  - `options`: 추가 요청 옵션
- `merchant_signature`: 판매자의 암호화 서명
- `timestamp`: 생성 시간

### CartMandate Artifact

A2A Artifact로 전달되는 CartMandate:

```json
{
  "name": "Fancy Cart Details",
  "artifactId": "artifact_001",
  "parts": [
    {
      "kind": "data",
      "data": {
        "ap2.mandates.CartMandate": {
          "contents": { /* CartMandate 내용 */ },
          "merchant_signature": "sig_merchant_shoes_abc1",
          "timestamp": "2025-08-26T19:36:36.377022Z"
        }
      }
    },
    {
      "kind": "data",
      "data": {
        "risk_data": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...fake_risk_data"
      }
    }
  ]
}
```

## 결제 흐름

### 1. 제품 검색 및 선택

```
User -> Shopping Agent: "Find me running shoes under $150"
Shopping Agent -> Merchant Agent: search_catalog(query="running shoes", max_price=150)
Merchant Agent -> Shopping Agent: [Product List]
Shopping Agent -> User: "Found 5 options. Nike Air Max 90 for $120?"
User -> Shopping Agent: "Yes, buy it"
```

### 2. 결제 방법 확인

```
Shopping Agent -> Credentials Provider: get_eligible_payment_methods()
Credentials Provider -> Shopping Agent: [Visa ending in 1234, Mastercard ending in 5678]
Shopping Agent -> User: "Pay with Visa 1234?"
User -> Shopping Agent: "Confirmed"
```

### 3. CartMandate 생성

```
Shopping Agent -> Merchant Agent: create_cart(items=[{id: "nike_air_max_90", qty: 1}])
Merchant Agent -> Shopping Agent: CartMandate (signed)
```

### 4. 결제 처리

```
Shopping Agent -> Payment Processor: process_payment(cartMandate, paymentMethod)
Payment Processor -> Bank: authorize_payment()
Bank -> Payment Processor: approved
Payment Processor -> Shopping Agent: payment_success
```

### 5. 주문 완료

```
Shopping Agent -> Merchant Agent: confirm_order(payment_proof)
Merchant Agent -> Shopping Agent: order_confirmed (tracking_number)
Shopping Agent -> User: "Order complete! Tracking: ABC123"
```

## 시퀀스 다이어그램

```
┌──────┐   ┌─────────────┐   ┌────────────┐   ┌─────────────┐   ┌──────────────┐
│ User │   │  Shopping   │   │  Merchant  │   │ Credentials │   │   Payment    │
│      │   │   Agent     │   │   Agent    │   │  Provider   │   │  Processor   │
└──┬───┘   └──────┬──────┘   └─────┬──────┘   └──────┬──────┘   └──────┬───────┘
   │              │                  │                 │                 │
   │ 1. Search    │                  │                 │                 │
   ├─────────────>│                  │                 │                 │
   │              │ 2. Query Catalog │                 │                 │
   │              ├─────────────────>│                 │                 │
   │              │<─────────────────┤                 │                 │
   │              │ 3. Products      │                 │                 │
   │<─────────────┤                  │                 │                 │
   │              │                  │                 │                 │
   │ 4. Buy       │                  │                 │                 │
   ├─────────────>│                  │                 │                 │
   │              │ 5. Get Methods   │                 │                 │
   │              ├────────────────────────────────────>│                 │
   │              │<────────────────────────────────────┤                 │
   │              │ 6. Select Method │                 │                 │
   │<─────────────┤                  │                 │                 │
   │ 7. Confirm   │                  │                 │                 │
   ├─────────────>│                  │                 │                 │
   │              │ 8. Create Cart   │                 │                 │
   │              ├─────────────────>│                 │                 │
   │              │<─────────────────┤                 │                 │
   │              │ 9. CartMandate   │                 │                 │
   │              │                  │                 │                 │
   │              │ 10. Process Payment                │                 │
   │              ├─────────────────────────────────────────────────────>│
   │              │                  │                 │                 │
   │              │<─────────────────────────────────────────────────────┤
   │              │ 11. Success      │                 │                 │
   │              │ 12. Confirm      │                 │                 │
   │              ├─────────────────>│                 │                 │
   │              │<─────────────────┤                 │                 │
   │              │ 13. Order #      │                 │                 │
   │<─────────────┤                  │                 │                 │
   │ Complete!    │                  │                 │                 │
```

## 보안 아키텍처

### 암호화 서명

**Merchant Signature**:
- 판매자가 CartMandate에 서명
- 가격, 항목 등 변조 방지
- 부인 불가능성 보장

**User Signature** (선택적):
- 고액 거래나 민감한 거래에 필요
- 사용자의 명시적 승인
- 법적 증거 제공

### OAuth2 인증 흐름

```
┌──────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────────┐
│ User │   │  Shopping   │   │ Credentials │   │   Auth       │
│      │   │   Agent     │   │  Provider   │   │   Server     │
└──┬───┘   └──────┬──────┘   └──────┬──────┘   └──────┬───────┘
   │              │                  │                 │
   │              │ 1. Request Auth  │                 │
   │              ├─────────────────>│                 │
   │              │                  │ 2. Auth URL     │
   │              │                  ├────────────────>│
   │              │<─────────────────┤                 │
   │              │ 3. Redirect      │                 │
   │              │                  │                 │
   │<──────────────────────────────────────────────────┤
   │              │ 4. Login         │                 │
   ├───────────────────────────────────────────────────>│
   │<───────────────────────────────────────────────────┤
   │              │ 5. Auth Code     │                 │
   │              │                  │                 │
   │              │ 6. Exchange Code │                 │
   │              ├─────────────────>│ 7. Verify       │
   │              │                  ├────────────────>│
   │              │                  │<────────────────┤
   │              │<─────────────────┤ 8. Access Token │
   │              │ 9. Token         │                 │
```

### Risk Data

거래 위험 평가를 위한 데이터:

```json
{
  "risk_data": {
    "ip_address": "192.168.1.1",
    "device_fingerprint": "abc123def456",
    "transaction_history": {
      "last_transaction": "2025-01-15",
      "total_transactions": 42,
      "average_amount": 85.50
    },
    "fraud_score": 0.12
  }
}
```

## 확장성

### 새로운 결제 방법 추가

AP2는 확장 가능한 설계:

```json
{
  "method_data": [
    {
      "supported_methods": "CRYPTO",
      "data": {
        "blockchain": "ethereum",
        "wallet_address": "0x..."
      }
    },
    {
      "supported_methods": "BANK_TRANSFER",
      "data": {
        "iban": "GB...",
        "swift": "..."
      }
    }
  ]
}
```

### 새로운 역할 추가

커뮤니티가 새로운 역할 정의 가능:
- `loyalty-provider`: 포인트/리워드 관리
- `shipping-provider`: 배송 서비스
- `insurance-provider`: 거래 보험

## 다음 단계

- [AP2 Implementation Guide](./ap2-implementation-guide.md) - 구현 가이드
- [AP2 Examples](./ap2-examples.md) - 예제 및 사용 사례
- [A2A Protocol](../a2a/a2a-protocol-overview.md) - A2A 프로토콜 이해
