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

---

## 🇰🇷 한국 결제 MCP

### 토스페이먼츠 MCP

> PG업계 최초 MCP 서버 (2025년 6월). **10분 만에 결제 연동 가능**

**시작하기:**
1. [토스페이먼츠 개발자센터](https://developers.tosspayments.com/sandbox) 가입
2. 테스트용 API 키 자동 발급
3. Sandbox에서 바로 테스트

**사용 예시:**
```
"결제창을 연결해줘"
"정기결제 연동하고 싶어"
→ AI가 연동 코드 생성
```

**특징:**
- Claude, Cursor 등 AI 코딩툴과 호환
- 결제 연동 문서/코드 생성 특화
- 회원가입만 하면 바로 테스트 가능

**참고:** [토스페이먼츠 MCP 구현기](https://toss.tech/article/tosspayments-mcp)

---

### 카카오페이 MCP Agent Toolkit

> 결제/정기결제 관련 **7개 API**를 자연어로 호출

**시작하기:**
1. [카카오페이 개발자센터](https://developers.kakaopay.com/) 가입
2. Sandbox 환경에서 테스트

**사용 예시:**
```
"5000원짜리 커피 결제 링크 생성해줘"
→ 실제 데모 결제 링크 생성됨
```

**지원 기능:**

| 기능 | 설명 |
|------|------|
| 결제 테스트 | 테스트 결제 실행 |
| 결제 준비 | 결제 링크 생성 |
| 결제 승인 | 결제 확정 |
| 결제 취소 | 환불 처리 |
| 상태 조회 | 결제 상태 확인 |
| 정기결제 | 구독 결제 |

**지원 프레임워크:**
- LangChain
- OpenAI SDK
- Vercel AI SDK

**참고:** [카카오페이 MCP 기술 블로그](https://tech.kakaopay.com/post/kakaopay-mcp-agent-toolkit/)

---

### 한국 vs 글로벌 비교

| 항목 | PayPal | 토스페이먼츠 | 카카오페이 |
|------|--------|-------------|-----------|
| **Sandbox** | ✓ | ✓ | ✓ |
| **MCP 용도** | 결제 API 호출 | 연동 코드 생성 | 결제 API 호출 |
| **시작 난이도** | 중간 | 쉬움 | 중간 |
| **한국 사용** | 제한적 | ⭐ 최적 | ⭐ 최적 |

---

## 참고

**글로벌:**
- PayPal Agent Toolkit: https://github.com/paypal/agent-toolkit
- PayPal MCP 문서: https://docs.paypal.ai/developer/tools/ai/mcp-quickstart
- Anthropic MCP: https://docs.anthropic.com/en/docs/claude-code/mcp

**한국:**
- 토스페이먼츠 개발자센터: https://developers.tosspayments.com/
- 카카오페이 개발자센터: https://developers.kakaopay.com/
