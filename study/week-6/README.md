# Week 6: 에이전틱 상거래 프로토콜

## 발표 개요

| 항목 | 내용 |
|------|------|
| **주제** | 에이전틱 상거래의 미래와 프로토콜 비교 |
| **시간** | 1시간 |
| **청중** | 개발자 + 비개발자 혼합 |
| **구성** | Why → What → How |

---

## 발표 순서

### 1. Why: 왜 에이전틱 상거래인가 (15분)

📄 **[presentation/01-why.md](presentation/01-why.md)**

- 기존 vs 에이전트 상거래 비교
- 시장 규모 (2030년 $3~5조)
- 빅플레이어 움직임 (Google, OpenAI, Visa, Mastercard)

### 2. What: 프로토콜 스택 (25분)

📄 **[presentation/02-what.md](presentation/02-what.md)**

- 전체 구조 다이어그램
- A2A + AP2: Mandate 시스템
- UCP: 상거래 전체 여정
- x402: Stateless 마이크로페이먼트
- 3종 비교표

### 3. How: 데모 시연 (15분)

📄 **[presentation/03-how.md](presentation/03-how.md)**

- x402 데모 (7분) - 자판기 비유
- A2A+AP2 데모 (8분) - 쇼핑몰 점원 비유

### 4. 마무리 + Q&A (5분)

- 핵심 요약
- 앞으로 주목할 점
- 예상 질문 답변

---

## 폴더 구조

```
week-6/
├── README.md                 # 발표 가이드 (현재 파일)
│
├── presentation/             # 📁 발표 자료
│   ├── 01-why.md            # Why: 시장 + 트렌드
│   ├── 02-what.md           # What: 프로토콜 스택
│   └── 03-how.md            # How: 데모 시연 가이드
│
├── reference/                # 📁 참조 자료 (심화)
│   ├── theory-ap2.md        # AP2 아키텍처 상세
│   ├── trends-full.md       # 최신 동향 전체
│   ├── a2a-ucp-relationship.md
│   ├── claude-mcp-commerce.md
│   └── code-examples.md     # 코드 예시
│
├── demos/                    # 📁 데모 코드
│   ├── a2a-ap2/             # A2A + AP2 데모
│   ├── ucp/                 # UCP 데모
│   ├── x402/                # x402 데모
│   └── mcp-commerce/        # MCP 상거래 데모
│
└── venv/                     # Python 가상환경
```

---

## 데모 실행 방법

### 사전 준비

```bash
cd study/week-6
source venv/bin/activate
```

가상환경이 없는 경우:
```bash
python -m venv venv
source venv/bin/activate
pip install flask httpx pytest
```

### x402 데모

```bash
# 터미널 1
cd demos/x402 && python server.py

# 터미널 2
cd demos/x402 && python client.py
```

### A2A + AP2 데모

```bash
# 터미널 1
cd demos/a2a-ap2 && python merchant_agent.py

# 터미널 2
cd demos/a2a-ap2 && python client_agent.py
```

### UCP 데모

```bash
# 터미널 1
cd demos/ucp && python merchant_server.py

# 터미널 2
cd demos/ucp && python client_demo.py
```

---

## 프로토콜 한눈에 보기

```
┌─────────────────────────────────────────────────────────┐
│              AI Agent (Claude, Gemini, ChatGPT)         │
├─────────────────────────────────────────────────────────┤
│    MCP (도구 연결)          │     A2A (에이전트 통신)     │
├─────────────────────────────────────────────────────────┤
│                         UCP                             │
│           (상거래: 검색 → 결제 → 주문관리)                │
├─────────────────────────────────────────────────────────┤
│    AP2 (결제 승인)          │     x402 (온체인 정산)     │
└─────────────────────────────────────────────────────────┘
```

| 프로토콜 | 용도 | 특징 |
|---------|------|------|
| **A2A + AP2** | 복잡한 에이전트 협업 | Mandate로 신뢰 확보 |
| **UCP** | 범용 상거래 | 전체 여정 커버 |
| **x402** | 마이크로페이먼트 | Stateless, 즉시 정산 |

---

## 참고 자료

### 공식 문서
- [A2A Protocol](https://a2a-protocol.org/latest/)
- [AP2 Protocol](https://ap2-protocol.org/)
- [UCP](https://ucp.dev/)
- [x402](https://docs.cdp.coinbase.com/x402/welcome)

### GitHub
- [google-agentic-commerce/AP2](https://github.com/google-agentic-commerce/AP2)
- [coinbase/x402](https://github.com/coinbase/x402)
- [Universal-Commerce-Protocol/ucp](https://github.com/Universal-Commerce-Protocol/ucp)

---

*작성일: 2026-01-26*
