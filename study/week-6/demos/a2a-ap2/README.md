# A2A + AP2 데모

## 개요

이 데모는 **A2A (Agent-to-Agent)** 프로토콜과 **AP2 (Agent Payments Protocol)**의 핵심 개념을 보여줍니다.

AP2는 Google이 PayPal, Mastercard, American Express, Coinbase 등 60개 이상의 기업과 협력하여 만든 AI 에이전트 결제 프로토콜입니다.

### 핵심 개념

1. **Agent Card**: 에이전트의 신원 및 기능 선언 (`/.well-known/agent-card.json`)
2. **Task**: 에이전트 간 작업 단위 (세션)
3. **Cart Mandate**: Merchant가 생성, User가 서명하는 결제 요청서
4. **Payment Mandate**: Agent가 생성, 결제 네트워크에 AI 관여 알림

### AP2 Mandate 체계

| Mandate | 생성자 | 서명자 | 시나리오 |
|---------|--------|--------|----------|
| Cart Mandate | Merchant | **User** | Human Present |
| Intent Mandate | Agent | **User** | Human NOT Present |
| Payment Mandate | Agent | Agent | 네트워크 알림 |

## 파일 구조

```
a2a-ap2/
├── merchant_agent.py      # 판매자 에이전트 (서버)
├── client_agent.py        # 쇼핑 에이전트 (클라이언트)
├── code_flow.md           # 상세 플로우 문서
├── test_a2a_unit.py       # 단위 테스트
├── test_a2a_integration.py # 통합 테스트
└── requirements.txt
```

## 실행 방법

```bash
# 가상환경 활성화 (week-6 루트에서)
source ../venv/bin/activate

# 터미널 1: 판매자 에이전트 실행
python merchant_agent.py

# 터미널 2: 쇼핑 에이전트 실행
python client_agent.py
```

## 시퀀스 다이어그램

```
[Client Agent]                    [Merchant Agent]
      │                                  │
      │ GET /.well-known/agent-card.json │
      │ ─────────────────────────────────>│  (1) 에이전트 발견
      │                                  │
      │ POST /a2a (tasks/create)         │
      │ ─────────────────────────────────>│  (2) 검색 태스크 생성
      │                                  │
      │         Cart Mandate             │
      │ <─────────────────────────────────│  (3) 결제 요청서 (Merchant 서명)
      │                                  │
      │  [User가 Cart Mandate 확인/서명]   │
      │                                  │
      │        Payment Mandate           │
      │ ─────────────────────────────────>│  (4) 결제 승인 + AI 관여 정보
      │                                  │
      │        Task Completed            │
      │ <─────────────────────────────────│  (5) 주문 완료
```

## 출력 예시

```
=== A2A + AP2 데모 시작 ===

[1] 에이전트 발견
    이름: Demo Merchant Agent
    AP2 지원: True

[2] 검색 태스크 생성
    Task ID: task_abc123
    검색어: 빨간 운동화

[3] Cart Mandate 수신
    상품: Nike Air Max 90 (Red)
    가격: $120.00

[4] Payment Mandate 전송
    Mandate ID: pm_xyz789
    Agent Initiated: True
    Human Present: True

[5] 결제 완료
    Transaction ID: tx_123456
    상태: completed

=== 데모 종료 ===
```

## 테스트 실행

```bash
# 단위 테스트
pytest test_a2a_unit.py -v

# 통합 테스트
pytest test_a2a_integration.py -v

# 전체 테스트
pytest -v
```

## 현재 구현의 한계 (데모용 단순화)

| 공식 스펙 | 현재 구현 |
|----------|----------|
| Cart Mandate에 User 서명 필요 | User 서명 생략 |
| 암호화 서명 검증 (ECDSA 등) | 시뮬레이션 |
| Intent Mandate 지원 | 미구현 |

자세한 플로우 설명은 [code_flow.md](./code_flow.md)를 참고하세요.

## 참고

- [AP2 Protocol Specification](https://ap2-protocol.org/specification/)
- [Google Cloud Blog - Announcing AP2](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol)
- [A2A Project](https://github.com/a2aproject/a2a-samples)
