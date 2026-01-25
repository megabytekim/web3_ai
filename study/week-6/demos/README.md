# Week 6 - 에이전틱 상거래 프로토콜 데모

## 개요

이 폴더는 에이전틱 상거래의 핵심 프로토콜들을 이해하기 위한 최소한의 데모 코드를 포함합니다.

| 폴더 | 프로토콜 | 핵심 개념 |
|------|---------|----------|
| `a2a-ap2/` | A2A + AP2 | 에이전트 간 통신 + 결제 Mandate |
| `ucp/` | UCP | 통합 상거래 프로토콜 (검색→결제→주문) |
| `x402/` | x402 | HTTP 402 기반 암호화폐 결제 |
| `mcp-commerce/` | MCP | Claude와 상거래 도구 연결 |

## 빠른 시작

```bash
# 공통 의존성 설치
pip install flask httpx pydantic

# 각 데모 실행
cd a2a-ap2 && python merchant_agent.py  # 터미널 1
cd a2a-ap2 && python client_agent.py    # 터미널 2
```

## 프로토콜 스택

```
┌─────────────────────────────────────────┐
│           AI Agent (Claude 등)           │
├─────────────────────────────────────────┤
│   MCP (도구 연결)  │  A2A (에이전트 통신)  │
├─────────────────────────────────────────┤
│                  UCP                     │
│        (상거래 기능: 검색/결제/주문)        │
├─────────────────────────────────────────┤
│          AP2 (결제 승인/Mandate)          │
├─────────────────────────────────────────┤
│        x402 (암호화폐 정산 레이어)         │
└─────────────────────────────────────────┘
```

## 참고 자료

### 공식 저장소
- [A2A Samples](https://github.com/a2aproject/a2a-samples) - 1.2k stars
- [AP2](https://github.com/google-agentic-commerce/AP2) - Google 공식
- [UCP Samples](https://github.com/Universal-Commerce-Protocol/samples) - Google 공식
- [x402](https://github.com/coinbase/x402) - 4.3k stars, Coinbase 공식
- [PayPal Agent Toolkit](https://github.com/paypal/agent-toolkit) - PayPal 공식

### 문서
- [A2A Protocol](https://a2a-protocol.org/latest/)
- [AP2 Protocol](https://ap2-protocol.org/)
- [UCP](https://ucp.dev/)
- [x402 Docs](https://docs.cdp.coinbase.com/x402/welcome)

---

*작성일: 2026-01-25*
