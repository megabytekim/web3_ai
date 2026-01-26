# UCP (Universal Commerce Protocol) 데모

## 개요

이 데모는 **UCP (Universal Commerce Protocol)**의 핵심 개념을 보여줍니다.

UCP는 2026년 1월 Google이 발표한 에이전틱 커머스를 위한 오픈 표준으로, Visa, Mastercard, Shopify, Target 등 20개 이상의 글로벌 파트너가 참여하고 있습니다.

### 핵심 개념

1. **Capability Profile**: `/.well-known/ucp.json`에서 지원 기능 선언
2. **Discovery Capability**: 상품 검색 및 조회
3. **Checkout Capability**: 결제 세션 생성 및 주문 처리
4. **Transport Agnostic**: REST, MCP, A2A 모두 지원

### A2A vs UCP

| 구분 | A2A + AP2 | UCP |
|------|-----------|-----|
| 발견 | Agent Card | Capability Profile |
| 통신 | JSON-RPC | REST API |
| 결제 | Mandate 시스템 | Checkout Session |
| 초점 | 에이전트 간 통신 | 범용 상거래 |

## 파일 구조

```
ucp/
├── merchant_server.py      # UCP 상점 서버
├── client_demo.py          # UCP 클라이언트 데모
├── sample_products.json    # 샘플 상품 데이터
├── code_flow.md            # 상세 플로우 문서
├── test_ucp_unit.py        # 단위 테스트
├── test_ucp_integration.py # 통합 테스트
└── requirements.txt
```

## 실행 방법

```bash
# 가상환경 활성화 (week-6 루트에서)
source ../venv/bin/activate

# 터미널 1: 상점 서버 실행
python merchant_server.py

# 터미널 2: 클라이언트 데모 실행
python client_demo.py
```

## UCP Capabilities

| Capability | 엔드포인트 | 설명 |
|------------|-----------|------|
| `discovery.product_search` | POST /ucp/discovery/search | 상품 검색 |
| `discovery.product_details` | GET /ucp/discovery/product/{id} | 상품 상세 조회 |
| `checkout.create_session` | POST /ucp/checkout/session | 결제 세션 생성 |
| `checkout.submit_order` | POST /ucp/checkout/submit | 주문 제출 |

## 시퀀스 다이어그램

```
[AI Agent]                      [UCP Merchant Server]
    │                                    │
    │ GET /.well-known/ucp.json          │
    │ ───────────────────────────────────>│  (1) Capability 발견
    │                                    │
    │ POST /ucp/discovery/search         │
    │ ───────────────────────────────────>│  (2) 상품 검색
    │                                    │
    │ POST /ucp/checkout/session         │
    │ ───────────────────────────────────>│  (3) 결제 세션 생성
    │         {session_id, total}        │
    │ <───────────────────────────────────│
    │                                    │
    │ POST /ucp/checkout/submit          │
    │ ───────────────────────────────────>│  (4) 주문 제출
    │                                    │
    │        Order Confirmation          │
    │ <───────────────────────────────────│  (5) 주문 확인
```

## 출력 예시

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

## 테스트 실행

```bash
# 단위 테스트
pytest test_ucp_unit.py -v

# 통합 테스트
pytest test_ucp_integration.py -v

# 전체 테스트
pytest -v
```

## 현재 구현의 한계 (데모용 단순화)

| 공식 스펙 | 현재 구현 |
|----------|----------|
| 다양한 Transport (REST, MCP, A2A) | REST만 구현 |
| Payment Handler 분리 | 직접 처리 (시뮬레이션) |
| Tokenized Payments | 토큰 검증 없음 |

자세한 플로우 설명은 [code_flow.md](./code_flow.md)를 참고하세요.

## 참고

- [UCP Official Documentation](https://ucp.dev/)
- [UCP Specification Overview](https://ucp.dev/specification/overview/)
- [GitHub - Universal-Commerce-Protocol/ucp](https://github.com/Universal-Commerce-Protocol/ucp)
