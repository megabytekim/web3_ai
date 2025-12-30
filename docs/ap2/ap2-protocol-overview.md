# Agent Payments Protocol (AP2) - Overview

## 소개

Agent Payments Protocol (AP2)은 신흥 Agent Economy에서 AI 에이전트 간 안전하고 신뢰할 수 있으며 상호 운용 가능한 커머스를 가능하게 하도록 설계된 개방형 프로토콜입니다.

## 핵심 정보

- **공식 사이트**: [ap2-protocol.org](https://ap2-protocol.org)
- **GitHub**: [github.com/ap2-protocol](https://github.com/ap2-protocol)
- **스펙 버전**: V0.1 (초기 릴리스)
- **라이선스**: Open Source
- **관계**: A2A 프로토콜의 확장(Extension)
- **목적**: AI 에이전트 자율 결제 지원

## AP2, A2A, MCP의 관계

AP2는 다른 에이전트 프로토콜들과 협력하여 작동합니다:

- **MCP (Model-Context Protocol)**: 에이전트가 데이터(API)와 통신
- **A2A (Agent-to-Agent)**: 에이전트가 다른 에이전트와 통신 (작업 및 메시지)
- **AP2 (Agent Payments)**: 에이전트가 결제에 대해 통신 (mandates)

```
┌─────────────────────────────────────────┐
│   사용자 (User)                          │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│   Shopping Agent (Shopper Role)         │
│   - MCP로 데이터 접근                    │
│   - A2A로 에이전트 통신                  │
│   - AP2로 결제 협상                      │
└─────────────┬───────────────────────────┘
              │
         ┌────┴────┐
         │         │
┌────────▼──┐  ┌──▼──────────┐
│ Merchant  │  │ Credentials │
│ Agent     │  │ Provider    │
└───────────┘  └─────────────┘
```

## 프로토콜의 목적

AP2는 다음을 가능하게 합니다:

1. **에이전트 자율 결제**: AI 에이전트가 사용자를 대신하여 안전하게 결제 수행
2. **개방성과 상호운용성**: 모든 호환 에이전트가 모든 호환 판매자와 작업 가능
3. **사용자 제어 및 프라이버시**: 사용자가 항상 최종 권한 보유
4. **검증 가능한 의도**: 사용자의 결정적이고 부인 불가능한 의도 증명
5. **명확한 거래 책임**: 거래 책임에 대한 명확한 추적 및 증명

## 4가지 핵심 역할

AP2 프로토콜은 4가지 에이전트 역할을 정의합니다:

### 1. Merchant (판매자)
판매자를 대표하는 에이전트:
- 제품/서비스 카탈로그 제공
- 결제 방법 정의
- CartMandate 생성 및 서명
- 주문 처리

### 2. Shopper (구매자)
사용자를 대신하여 쇼핑하는 에이전트:
- 제품 검색 및 비교
- 장바구니 관리
- 결제 방법 선택
- 거래 완료

### 3. Credentials Provider (자격증명 제공자)
사용자의 결제 정보를 보관하는 에이전트:
- 사용자 결제 방법 관리
- 배송 주소 제공
- 안전한 자격증명 처리
- OAuth2 인증 지원

### 4. Payment Processor (결제 처리자)
실제 결제를 처리하는 에이전트:
- 결제 승인 처리
- 거래 검증
- 결제 완료 확인

## 핵심 지침 원칙

### 개방성과 상호운용성 (Openness and Interoperability)
- 개방형, 비독점적 프로토콜
- 경쟁적 환경 조성
- 모든 호환 에이전트가 모든 호환 판매자와 작업 가능

### 사용자 제어 및 프라이버시 (User Control and Privacy)
- 사용자가 항상 최종 권한 보유
- 프라이버시 우선 설계
- 역할 기반 아키텍처
- 민감한 데이터 암호화

### 검증 가능한 의도 (Verifiable Intent, Not Inferred Action)
- 신뢰는 결정적이고 부인 불가능한 사용자 의도 증명에 기반
- 에이전트 오류나 "환각(hallucination)" 위험 직접 해결
- 암호화 서명을 통한 의도 증명

### 명확한 거래 책임 (Clear Transaction Accountability)
- 거래 책임에 대한 명확성
- 부인 불가능한 암호화 감사 추적
- 분쟁 해결을 위한 증거 제공
- VDC(Verifiable Data Credential) 프레임워크 지원

## 핵심 개념

### CartMandate (장바구니 위임장)

CartMandate는 합의된 거래 세부사항의 증거입니다:

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
            "label": "Nike Air Max 90",
            "amount": {
              "currency": "USD",
              "value": 120.0
            }
          }
        ],
        "total": {
          "label": "Total",
          "amount": {
            "currency": "USD",
            "value": 120.0
          }
        }
      }
    }
  },
  "merchant_signature": "sig_merchant_shoes_abc1",
  "timestamp": "2025-08-26T19:36:36.377022Z"
}
```

### 지원 결제 방법

#### V0.1 (현재)
- **Pull Payments**: 신용/직불 카드
- **Human-Present**: 사용자가 거래 시 참여
- **Step-up Challenges**: 추가 인증 지원

#### V1.x (계획)
- **Push Payments**: 실시간 은행 이체, 전자지갑
- **구독 및 반복 결제**: 표준화된 흐름
- **Human-Not-Present**: 완전 자율 거래

#### Long-Term Vision
- 복잡한 다중 판매자 거래 토폴로지
- 구매자-판매자 에이전트 간 실시간 협상
- 디지털 화폐 지원

## A2A Extension으로서의 AP2

AP2는 A2A 프로토콜의 공식 확장입니다:

### Agent Card에 AP2 선언

```json
{
  "name": "MerchantAgent",
  "description": "A sales assistant agent for a merchant.",
  "capabilities": {
    "extensions": [
      {
        "description": "Supports the A2A payments extension.",
        "required": true,
        "uri": "https://google-a2a.github.io/A2A/ext/payments/v1"
      },
      {
        "description": "Supports the Visa payment method extension",
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
  "url": "http://example.com/a2a/merchant_agent",
  "version": "1.0.0"
}
```

### AP2 Extension Parameters

```json
{
  "type": "object",
  "properties": {
    "roles": {
      "type": "array",
      "minItems": 1,
      "items": {
        "enum": ["merchant", "shopper", "credentials-provider", "payment-processor"]
      }
    }
  },
  "required": ["roles"]
}
```

## 보안 및 신뢰

### 암호화 서명
- **Merchant Signature**: 판매자가 CartMandate에 서명
- **User Signature**: 사용자가 결제 의도 확인 (선택적)
- **Non-repudiable**: 부인 불가능한 거래 증명

### OAuth2 인증
Credentials Provider는 OAuth2를 사용하여 안전한 인증 제공:

```json
{
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
            "get_payment_methods": "description"
          },
          "tokenUrl": "http://example.com/token"
        }
      },
      "type": "oauth2"
    }
  }
}
```

### Risk Data
거래 위험 평가를 위한 추가 데이터:
- 사기 탐지
- 거래 검증
- 규정 준수

## AP2와 X402

AP2는 결제 방법에 구애받지 않도록 설계되었습니다:

- **X402**: Web3 결제 프로토콜 (암호화폐, 블록체인)
- **AP2**: 모든 결제 방법 지원 (카드, 은행 이체, 디지털 화폐)
- **Future-Proof**: 새로운 결제 방식도 지원 가능하도록 확장 가능

## 로드맵

### V0.1 (현재)
- Pull 결제 방법 지원 (신용/직불 카드)
- VDC 프레임워크 기반 명확한 책임 추적
- Human-present 시나리오 지원
- Step-up 챌린지 지원
- A2A 프로토콜 기반 참조 구현

### V1.x (향후)
- Push 결제 완전 지원 (실시간 은행 이체, 전자지갑)
- 구독 및 반복 결제 표준화
- Human-not-present 시나리오 지원
- MCP 기반 구현 상세 시퀀스 다이어그램

### Long-Term Vision
- 복잡한 다중 판매자 거래 토폴로지
- 구매자-판매자 에이전트 간 실시간 협상
- 더 많은 지능과 유연성

## 사용 사례

### 1. 자율 쇼핑
Shopping Agent가 사용자를 대신하여:
- 최적의 제품 검색
- 가격 비교
- 자동 구매
- 배송 추적

### 2. 구독 관리
- 자동 갱신
- 최적 요금제 협상
- 구독 취소/변경
- 비용 최적화

### 3. B2B 거래
- 대량 구매 협상
- 공급망 자동화
- 청구서 처리
- 재고 관리

### 4. 크로스 플랫폼 결제
- 여러 판매자 통합 결제
- 통일된 결제 경험
- 단일 인증으로 여러 서비스 이용

## 시작하기

### 1. A2A 프로토콜 이해
AP2는 A2A의 확장이므로, 먼저 A2A 프로토콜을 이해해야 합니다:
- [A2A Protocol Overview](../a2a/a2a-protocol-overview.md)
- [A2A Architecture](../a2a/a2a-architecture.md)

### 2. 역할 선택
구현하고자 하는 역할 선택:
- Merchant Agent
- Shopping Agent (Shopper)
- Credentials Provider
- Payment Processor

### 3. Agent Card 구성
선택한 역할에 맞게 Agent Card에 AP2 Extension 선언

### 4. 구현
역할별 스킬 및 메시지 핸들러 구현

## 참고 자료

- [공식 웹사이트](https://ap2-protocol.org)
- [GitHub 저장소](https://github.com/ap2-protocol)
- [A2A Protocol](../a2a/a2a-protocol-overview.md)
- [AP2 Specification](https://github.com/context7/ap2-protocol/blob/main/specification.md)

## 다음 단계

- [AP2 Architecture](./ap2-architecture.md) - 아키텍처 및 핵심 개념
- [AP2 Implementation Guide](./ap2-implementation-guide.md) - 구현 가이드
- [AP2 Examples](./ap2-examples.md) - 예제 및 사용 사례
