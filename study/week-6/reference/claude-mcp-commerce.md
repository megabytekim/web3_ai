# Claude MCP 기반 상거래 통합 사례

## 개요

Anthropic의 Claude는 **Model Context Protocol (MCP)**를 통해 다양한 상거래 도구와 통합됩니다. MCP는 AI 모델이 외부 시스템(데이터베이스, API, 비즈니스 도구)과 연결하는 인프라 수준의 프로토콜입니다.

---

## 1. Anthropic 공식 Connectors Directory

### 접근 방법
- **URL**: [claude.ai/directory](https://claude.ai/directory)
- **요구사항**: Pro, Max, Team, Enterprise 플랜 (무료 플랜 제외)
- **연결 방식**: OAuth 인증을 통한 원클릭 연결

### 상거래 관련 공식 Connectors

| Connector | 기능 |
|-----------|------|
| **Stripe** | 고객 데이터, 결제 정보, 환불 처리 |
| **PayPal** | 거래 인사이트, 청구서 관리, 분쟁 처리 |
| **Shopify** | 상품 관리, 주문 처리, 고객 관리 |

> 출처: [Anthropic Connectors Directory](https://www.anthropic.com/news/connectors-directory)

---

## 2. PayPal MCP 통합

### 2.1 개요

PayPal은 2025년 4월부터 MCP 서버를 공식 출시하여 에이전틱 상거래를 지원합니다.

### 2.2 연결 방식

| 방식 | 설명 |
|------|------|
| **Remote MCP Server** | claude.ai/directory에서 원클릭 연결 |
| **Local MCP Server** | PayPal Agent Toolkit 다운로드 후 로컬 실행 |

### 2.3 지원 기능

```
├── Payments (결제)
│   ├── 결제 처리
│   ├── 거래 조회
│   └── 환불 처리
├── Invoices (청구서)
│   ├── 청구서 생성
│   ├── 청구서 전송
│   └── 청구서 상태 조회
├── Disputes (분쟁)
│   ├── 분쟁 조회
│   └── 분쟁 대응
├── Subscriptions (구독)
│   ├── 구독 관리
│   └── 정기 결제
├── Shipment Tracking (배송)
│   └── 배송 추적
└── Reporting (리포팅)
    ├── 거래 인사이트
    └── 매출 분석
```

### 2.4 사용 예시

```
User: "Create a PayPal invoice link for painting a house
       with a cost of $450. Add 8% tax and apply 5% discount.
       Make sure it expires in 10 days."

Claude: [PayPal MCP를 통해 청구서 생성 및 링크 반환]
```

### 2.5 주요 파트너십

PayPal Dev Days 2025에서 발표된 협력사:
- Amazon Web Services
- **Anthropic**
- Google Cloud
- Microsoft

> 출처:
> - [PayPal MCP Rollout](https://developer.paypal.com/community/blog/paypal-model-context-protocol/)
> - [PayPal in Claude](https://developer.paypal.com/community/blog/paypal-integration-in-claude/)

---

## 3. Stripe MCP 통합

### 3.1 Agent Skills

Anthropic은 2025년 12월 **Agent Skills**를 발표하며 Stripe를 포함한 10개 파트너 Skills를 공개했습니다.

**Stripe Best Practices Skill 포함 내용:**
- 결제 처리 (CheckoutSessions, PaymentIntents)
- 구독 관리
- Webhook 설정
- Connect 플랫폼
- 오류 처리 및 보안

### 3.2 지원 기능

| 기능 | API |
|------|-----|
| **결제 세션 생성** | CheckoutSessions |
| **결제 의도 처리** | PaymentIntents |
| **고객 관리** | Customers |
| **구독 관리** | Subscriptions |
| **환불 처리** | Refunds |

### 3.3 Claude Desktop 설정 예시

```json
{
  "mcpServers": {
    "stripe": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-stripe"],
      "env": {
        "STRIPE_API_KEY": "sk_test_..."
      }
    }
  }
}
```

> 출처: [Stripe Best Practices Skill](https://mcpservers.org/claude-skills/stripe/stripe-best-practices)

---

## 4. Shopify MCP 통합

### 4.1 사용 가능한 MCP 서버

| 저장소 | 언어 | 특징 |
|--------|------|------|
| [GeLi2001/shopify-mcp](https://github.com/GeLi2001/shopify-mcp) | TypeScript | GraphQL API, 상품/주문/고객 관리 |
| [pashpashpash/shopify-mcp-server](https://github.com/pashpashpash/shopify-mcp-server) | TypeScript | 상품/고객/주문 관리 |
| [siddhantbajaj/shopify-mcp-server](https://github.com/siddhantbajaj/shopify-mcp-server) | Python | Python 3.12+, 기본 조회 |
| [antoineschaller/shopify-mcp-server](https://github.com/antoineschaller/shopify-mcp-server) | TypeScript | **22개 도구**, 포괄적 기능 |
| [Shopify Dev MCP](https://shopify.dev/docs/apps/build/devmcp) | 공식 | 문서/API 스키마 접근 |

### 4.2 주요 기능

```
├── Product Management (상품 관리)
│   ├── 상품 목록 조회
│   ├── 상품 생성/수정/삭제
│   ├── 변형(Variants) 관리
│   └── 이미지 관리
├── Order Management (주문 관리)
│   ├── 주문 목록 조회
│   ├── 주문 상세 조회
│   ├── 주문 생성
│   └── 주문 이행(Fulfillment)
├── Customer Management (고객 관리)
│   ├── 고객 목록 조회
│   ├── 고객 생성/수정
│   └── 고객 검색
├── Collection Management (컬렉션 관리)
│   ├── 컬렉션 조회
│   └── 상품-컬렉션 연결
└── Inventory (재고)
    ├── 재고 수준 조회
    └── 재고 조정
```

### 4.3 Claude Desktop 설정 예시

```json
{
  "mcpServers": {
    "shopify": {
      "command": "npx",
      "args": ["-y", "shopify-mcp"],
      "env": {
        "SHOPIFY_STORE_URL": "your-store.myshopify.com",
        "SHOPIFY_ACCESS_TOKEN": "shpat_..."
      }
    }
  }
}
```

### 4.4 사용 예시

```
User: "내 Shopify 스토어에서 재고가 10개 미만인 상품 목록을 보여줘"

Claude: [Shopify MCP를 통해 재고 조회 후 결과 반환]

User: "Nike Air Max 상품의 가격을 $120에서 $99로 변경해줘"

Claude: [Shopify MCP를 통해 상품 가격 업데이트]
```

> 출처: [Composio Shopify MCP](https://composio.dev/toolkits/shopify/framework/claude-code)

---

## 5. WooCommerce MCP 통합

### 5.1 사용 가능한 MCP 서버

| 이름 | 특징 |
|------|------|
| [WooCommerce 공식 MCP](https://developer.woocommerce.com/docs/features/mcp/) | 네이티브 지원 (개발자 프리뷰) |
| [MCP for WooCommerce](https://woo-mcp.com/) | WordPress 플러그인, 읽기 전용 |
| [CData WooCommerce MCP](https://github.com/CDataSoftware/woocommerce-mcp-server-by-cdata) | JDBC 기반, SQL 쿼리 지원 |
| [UCP Connect for WooCommerce](https://lobehub.com/mcp/joellobo1234-ucp-connect-woocommerce) | UCP + MCP 통합 |

### 5.2 UCP Connect for WooCommerce

특히 주목할 만한 것은 **UCP Connect for WooCommerce**입니다:

- WooCommerce를 **UCP (Universal Commerce Protocol)**와 **MCP** 모두를 통해 노출
- AI 에이전트가 상품 검색, 발견, 구매까지 가능
- Claude Desktop 및 브라우저 기반 AI 어시스턴트 지원

> 출처: [WooCommerce MCP Documentation](https://developer.woocommerce.com/docs/features/mcp/)

---

## 6. BigCommerce MCP 통합

### 6.1 사용 가능한 MCP 서버

| 저장소 | 특징 |
|--------|------|
| [CData BigCommerce MCP](https://github.com/CDataSoftware/bigcommerce-mcp-server-by-cdata) | 읽기 전용, JDBC 기반 |
| [isaacgounton/bigcommerce-api-mcp](https://github.com/isaacgounton/bigcommerce-api-mcp) | BigCommerce API 통합 |

### 6.2 Claude Desktop 설정

```json
{
  "mcpServers": {
    "bigcommerce": {
      "command": "node",
      "args": ["path/to/mcpServer.js"],
      "env": {
        "BIGCOMMERCE_STORE_HASH": "your-store-hash",
        "BIGCOMMERCE_API_KEY": "your-api-key"
      }
    }
  }
}
```

---

## 7. 암호화폐 결제 MCP

### 7.1 사용 가능한 서버

| 이름 | 기능 |
|------|------|
| **Bitcoin Lightning MCP** | Lightning 네트워크를 통한 즉시 결제 |
| **AgentPMT** | USDC 스테이블코인 결제 (Base 블록체인) |

### 7.2 x402 프로토콜 연동

x402 프로토콜은 MCP와 통합하여 AI 에이전트의 암호화폐 결제를 지원합니다:

```
[AI Agent] → [MCP Server] → [x402 Facilitator] → [Blockchain]
```

---

## 8. 프로토콜 관계 정리

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude / AI Agent                        │
├─────────────────────────────────────────────────────────────┤
│                          MCP                                 │
│        (Model Context Protocol - 도구 연결 표준)              │
├──────────────┬──────────────┬──────────────┬───────────────┤
│   Shopify    │   PayPal     │   Stripe     │  WooCommerce  │
│   MCP Server │   MCP Server │   MCP Server │   MCP Server  │
├──────────────┴──────────────┴──────────────┴───────────────┤
│                         ACP / UCP                            │
│              (상거래 특화 프로토콜 - 체크아웃)                  │
├─────────────────────────────────────────────────────────────┤
│                       AP2 / x402                             │
│                    (결제 승인 / 정산)                         │
└─────────────────────────────────────────────────────────────┘
```

### 프로토콜별 역할

| 프로토콜 | 역할 | 레이어 |
|---------|------|--------|
| **MCP** | AI ↔ 외부 도구 연결 | 인프라 |
| **ACP** | 체크아웃, 결제 흐름 | 상거래 |
| **UCP** | 전체 상거래 여정 | 상거래 |
| **AP2** | 결제 승인, Mandate | 결제 |
| **x402** | 암호화폐 정산 | 결제 |

---

## 9. 업계 채택 현황

### 9.1 주요 플랫폼 MCP 지원

| 플랫폼 | MCP 지원 시점 | 비고 |
|--------|--------------|------|
| Shopify | 2025년 여름 | 100만+ 스토어 |
| commercetools | 2025년 | 엔터프라이즈 |
| WooCommerce | 2025년 | 개발자 프리뷰 |
| BigCommerce | 2025년 | 커뮤니티 서버 |

### 9.2 결제사 파트너십

| 결제사 | AI 파트너 |
|--------|----------|
| **Visa** | Anthropic, Microsoft, Mistral, OpenAI, Perplexity |
| **Mastercard** | Microsoft, IBM |
| **PayPal** | Anthropic, AWS, Google Cloud, Microsoft |

> 출처: [Fortune - MCP and E-commerce](https://fortune.com/2025/05/15/mcp-model-context-protocol-anthropic-ai-retail-revolution-shopping-ecommerce-ai-agents/)

---

## 10. 실습: Claude Desktop에서 상거래 MCP 설정

### 10.1 설정 파일 위치

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 10.2 복합 상거래 MCP 설정 예시

```json
{
  "mcpServers": {
    "shopify": {
      "command": "npx",
      "args": ["-y", "shopify-mcp"],
      "env": {
        "SHOPIFY_STORE_URL": "your-store.myshopify.com",
        "SHOPIFY_ACCESS_TOKEN": "shpat_xxx"
      }
    },
    "paypal": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-paypal"],
      "env": {
        "PAYPAL_CLIENT_ID": "your-client-id",
        "PAYPAL_CLIENT_SECRET": "your-client-secret"
      }
    },
    "stripe": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-stripe"],
      "env": {
        "STRIPE_API_KEY": "sk_test_xxx"
      }
    }
  }
}
```

### 10.3 연결 확인

Claude Desktop 재시작 후:
1. MCP 섹션에서 각 서버 옆에 녹색 원 확인
2. "My Shopify store products" 등의 프롬프트로 테스트

---

## 11. 참고 자료

### 공식 문서
- [Anthropic MCP Documentation](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Anthropic Connectors Directory](https://www.anthropic.com/partners/mcp)
- [PayPal MCP Quickstart](https://docs.paypal.ai/developer/tools/ai/mcp-quickstart)
- [Shopify Dev MCP](https://shopify.dev/docs/apps/build/devmcp)
- [WooCommerce MCP](https://developer.woocommerce.com/docs/features/mcp/)

### GitHub 저장소
- [Shopify MCP](https://github.com/GeLi2001/shopify-mcp)
- [PayPal Agent Toolkit](https://github.com/paypal/agent-toolkit)
- [BigCommerce MCP](https://github.com/CDataSoftware/bigcommerce-mcp-server-by-cdata)
- [WooCommerce MCP](https://github.com/CDataSoftware/woocommerce-mcp-server-by-cdata)

### 블로그 및 기사
- [PayPal Integration in Claude](https://developer.paypal.com/community/blog/paypal-integration-in-claude/)
- [MCP for Agentic Commerce](https://glama.ai/blog/2025-07-18-building-a-mcp-server-for-agentic-commerce-pay-pal-edition)
- [Anthropic Agent Skills Launch](https://venturebeat.com/technology/anthropic-launches-enterprise-agent-skills-and-opens-the-standard)

---

*작성일: 2026-01-25*
*Week 6 보충 자료 - Claude MCP 상거래 통합*
