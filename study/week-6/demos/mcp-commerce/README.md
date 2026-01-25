# MCP Commerce 데모

## 개요

이 데모는 **Claude**와 **MCP (Model Context Protocol)**를 통한 상거래 통합을 보여줍니다.
실제 결제 없이 PayPal Sandbox 모드로 테스트할 수 있습니다.

### 핵심 개념

1. **MCP Server**: Claude가 외부 도구에 접근하는 표준 프로토콜
2. **PayPal Agent Toolkit**: PayPal API를 MCP로 노출
3. **Sandbox Mode**: 실제 결제 없이 테스트

## 파일 구조

```
mcp-commerce/
├── claude_config.json    # Claude Desktop 설정 예시
├── example_prompts.md    # 테스트용 프롬프트 모음
└── README.md
```

## 설정 방법

### 1. PayPal Sandbox 계정 생성

1. https://developer.paypal.com 접속
2. Sandbox 계정 생성
3. Client ID / Secret 발급

### 2. Claude Desktop 설정

`claude_desktop_config.json` 파일 위치:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "paypal": {
      "command": "npx",
      "args": ["-y", "@paypal/mcp", "--tools=all"],
      "env": {
        "PAYPAL_CLIENT_ID": "your-sandbox-client-id",
        "PAYPAL_CLIENT_SECRET": "your-sandbox-secret",
        "PAYPAL_ENVIRONMENT": "SANDBOX"
      }
    }
  }
}
```

### 3. Claude Desktop 재시작

설정 후 Claude Desktop을 재시작하면 PayPal MCP 서버가 연결됩니다.

## 사용 방법

Claude에서 PayPal 관련 질문을 하면 MCP를 통해 실제 API를 호출합니다:

```
사용자: "내 PayPal 계정의 최근 거래 내역을 보여줘"
Claude: [PayPal MCP를 통해 거래 내역 조회]

사용자: "홍길동에게 $10 청구서를 만들어줘"
Claude: [PayPal MCP를 통해 청구서 생성]
```

## MCP 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                    Claude                           │
│            (AI Assistant)                           │
├─────────────────────────────────────────────────────┤
│                     MCP                             │
│        (Model Context Protocol)                     │
├──────────────┬──────────────┬──────────────────────┤
│   PayPal     │   Stripe     │   Shopify            │
│   MCP Server │   MCP Server │   MCP Server         │
├──────────────┼──────────────┼──────────────────────┤
│   PayPal     │   Stripe     │   Shopify            │
│   API        │   API        │   API                │
└──────────────┴──────────────┴──────────────────────┘
```

## 지원 기능 (PayPal MCP)

| 기능 | 설명 |
|------|------|
| `get_transaction_info` | 거래 정보 조회 |
| `list_transactions` | 거래 내역 목록 |
| `create_invoice` | 청구서 생성 |
| `send_invoice` | 청구서 전송 |
| `list_invoices` | 청구서 목록 |
| `create_order` | 주문 생성 |
| `capture_order` | 주문 결제 |
| `list_disputes` | 분쟁 목록 |
| `get_tracking_info` | 배송 추적 |

## 참고

- PayPal Agent Toolkit: https://github.com/paypal/agent-toolkit
- PayPal MCP 문서: https://www.paypal.ai/docs/tools/agent-toolkit-quickstart
- Anthropic MCP: https://docs.anthropic.com/en/docs/claude-code/mcp
