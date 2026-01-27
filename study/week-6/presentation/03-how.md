# 3. How: 데모 시연

## 사전 준비

### 가상환경 설정

```bash
cd /path/to/web3_ai/study/week-6

# 가상환경이 없으면 생성
python -m venv venv
source venv/bin/activate
pip install flask httpx pytest
```

이미 venv가 있으면 활성화만:
```bash
source venv/bin/activate
```

### 터미널 2개 준비

- **터미널 1**: 서버 실행용
- **터미널 2**: 클라이언트 실행용

---

## 데모 1: x402

> **왜 먼저?**: 가장 단순해서 개념 잡기 좋음

### 핵심 메시지

> "자판기에 동전 넣으면 음료 나오는 것처럼,
> X-PAYMENT 헤더 보내면 데이터 나옵니다."

### 실행

**터미널 1 (서버)**
```bash
cd demos/x402
python server.py
```

**터미널 2 (클라이언트)**
```bash
cd demos/x402
python client.py
```

### 예상 출력

```
=== x402 데모: 결제 클라이언트 ===

[테스트 1] 무료 API 호출
  ✓ 성공 (무료)

[테스트 2] 유료 API 호출 ($0.10)
  ⚠ 402 Payment Required       ← 여기서 멈춰서 설명!
  결제 요청:
    - 금액: $0.10 USDC
    - 네트워크: base
  → X-PAYMENT 헤더와 함께 재요청
  ✓ 결제 성공!

[테스트 3] AI 분석 API 호출 ($0.50)
  ⚠ 402 Payment Required
  → X-PAYMENT 헤더와 함께 재요청
  ✓ 결제 성공!

=== 데모 종료 ===
```

| 시점 | 설명할 내용 |
|------|------------|
| `402 Payment Required` | "서버가 결제 요구. HTTP 표준 상태코드" |
| `X-PAYMENT 헤더` | "결제 정보를 Base64로 인코딩해서 전송" |
| `✓ 결제 성공` | "Stateless - 매번 독립적으로 결제" |

- **세션 없음**: 로그인도 장바구니도 없음
- **즉시 정산**: 실제로는 2초 내 온체인 처리
- **용도**: API 수익화, 마이크로페이먼트

---

## 데모 2: A2A + AP2

> **왜 두 번째?**: x402보다 복잡하지만, 실제 쇼핑 시나리오

### 핵심 메시지

> "쇼핑몰에서 점원과 대화하며 구매하는 것처럼,
> 에이전트가 협상하고 장바구니 만들고 결제합니다."

### 실행

**터미널 1 (판매자 에이전트)**
```bash
cd demos/a2a-ap2
python merchant_agent.py
```

**터미널 2 (클라이언트 에이전트)**
```bash
cd demos/a2a-ap2
python client_agent.py
```

### 예상 출력

```
=== A2A + AP2 데모: 쇼핑 에이전트 ===

[Step 1] Agent Card 발견
  ✓ Merchant: Demo Flower Shop
  ✓ Skills: ['product-search', 'checkout']

[Step 2] Task 생성 및 상품 검색
  ✓ Task ID: task_abc123
  ✓ 검색 결과: Red Rose Bouquet - $45.00

[Step 3] 장바구니 생성         ← 여기서 멈춰서 설명!
  ✓ Cart ID: cart_xyz789

[Step 4] Cart Mandate 수신     ← 핵심 포인트!
  ✓ Mandate ID: mandate_001
  ✓ 서명 필요: 사용자 확인 대기

[Step 5] Payment Mandate 생성 및 결제
  ✓ 결제 완료
  ✓ Order ID: order_final123

=== 데모 종료 ===
```

### 설명 포인트

| 시점 | 설명할 내용 |
|------|------------|
| `Agent Card 발견` | "에이전트가 서로를 어떻게 찾는지" |
| `Task 생성` | "세션 개념. 대화가 이어짐" |
| `Cart Mandate` | "판매자가 만들고, 사용자가 서명해야 결제 가능" |
| `Payment Mandate` | "결제망에 AI 에이전트 개입 여부 전달" |

### x402와 비교

| | x402 | A2A + AP2 |
|---|------|-----------|
| **상태** | Stateless | Stateful (Task) |
| **장바구니** | ❌ | ✓ |
| **환불** | 어려움 | 가능 |
| **복잡도** | 낮음 | 높음 |

---

## 데모 3: UCP

> **왜 마지막?**: A2A와 비교하며 "더 단순한 대안"을 보여줌

### 핵심 메시지

> "기존 쇼핑몰에 AI 연동하려면 UCP가 더 쉽습니다.
> REST API만 쓰면 되니까요."

### 실행

**터미널 1 (상점 서버)**
```bash
cd demos/ucp
python merchant_server.py
```

**터미널 2 (클라이언트)**
```bash
cd demos/ucp
python client_demo.py
```

### 예상 출력

```
=== UCP 데모: 쇼핑 클라이언트 ===

[Step 1] UCP Capability 발견
  ✓ 상점: Demo Flower Shop
  ✓ Discovery 지원: True
  ✓ Checkout 지원: True

[Step 2] 상품 검색
  ✓ 검색 결과: 1개
    - Red Rose Bouquet: $45.00

[Step 3] 결제 세션 생성
  ✓ Session ID: session_abc123
  ✓ 총액: $50.00

[Step 4] 주문 제출
  ✓ Order ID: order_xyz789
  ✓ 상태: confirmed

=== 데모 종료 ===
```

### 설명 포인트

| 시점 | 설명할 내용 |
|------|------------|
| `Capability 발견` | "/.well-known/ucp.json에서 지원 기능 확인" |
| `상품 검색` | "REST API로 검색. 기존 쇼핑몰 API와 유사" |
| `Checkout Session` | "Mandate 대신 세션 기반. 웹 결제와 비슷" |

### A2A + AP2와 비교

| 구분 | A2A + AP2 | UCP |
|------|-----------|-----|
| **발견** | Agent Card | Capability Profile |
| **통신** | JSON-RPC | REST API |
| **결제** | Mandate 시스템 | Checkout Session |
| **적합** | 에이전트 간 협업 | 기존 쇼핑몰 연동 |

> **핵심**: UCP는 A2A를 대체하지 않음. 기존 시스템과 통합이 쉬운 **실용적 선택지**

---

## 마무리

### 핵심 요약

```
┌─────────────────────────────────────────────────────┐
│  에이전틱 상거래 = AI가 대신 쇼핑                      │
├─────────────────────────────────────────────────────┤
│  • 복잡한 거래 → A2A + AP2 (Mandate로 신뢰 확보)     │
│  • 범용 상거래 → UCP (검색~주문관리 전체)             │
│  • 간단한 결제 → x402 (Stateless, 마이크로페이먼트)   │
├─────────────────────────────────────────────────────┤
│  2030년 조 단위 시장, 지금 표준 경쟁 중               │
└─────────────────────────────────────────────────────┘
```

### 앞으로 주목할 점

1. **프로토콜 통합**: ACP(OpenAI) vs AP2/UCP(Google) 경쟁과 상호운용성
2. **보안**: KYA (Know Your Agent), 에이전트 신원 검증
3. **규제**: EU AI Act, 제조물 책임 (2026년 12월 시행)
4. **책임 소재**: 에이전트 오류 시 누가 책임지나?

### 참고 자료

- **공식 문서**: [a2a-protocol.org](https://a2a-protocol.org), [ap2-protocol.org](https://ap2-protocol.org), [ucp.dev](https://ucp.dev), [x402.org](https://x402.org)
- **GitHub**: [github.com/coinbase/x402](https://github.com/coinbase/x402), [github.com/google-agentic-commerce](https://github.com/google-agentic-commerce)

---

## Q&A

예상 질문:

| 질문 | 답변 |
|------|------|
| "실제 결제는 어떻게?" | "데모는 시뮬레이션. 실제는 Coinbase CDP, Stripe 등 연동" |
| "언제 상용화?" | "Visa/Mastercard 2026 Q1 예정, ChatGPT Instant Checkout은 이미 시작" |
| "어떤 프로토콜이 이길까?" | "단일 승자보다 상호운용성이 핵심. 용도별로 공존 가능" |

---

*데모 상세: [demos/x402/code_flow.md](../demos/x402/code_flow.md), [demos/a2a-ap2/code_flow.md](../demos/a2a-ap2/code_flow.md)*
