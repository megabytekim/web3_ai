# UCP (Universal Commerce Protocol) 데모

## 개요

이 데모는 **UCP (Universal Commerce Protocol)**의 핵심 개념을 보여줍니다.
UCP는 상거래 여정 전체(검색 → 장바구니 → 결제 → 주문관리)를 위한 통합 프로토콜입니다.

### 핵심 개념

1. **Capabilities**: 비즈니스가 제공하는 기능 선언 (Checkout, Discovery 등)
2. **Capability Profile**: `/.well-known/ucp.json`에서 지원 기능 노출
3. **Checkout Session**: 결제 세션 생성 및 관리
4. **Transport Agnostic**: REST, MCP, A2A 모두 지원

## 파일 구조

```
ucp/
├── merchant_server.py    # UCP 상점 서버
├── client_demo.py        # UCP 클라이언트 데모
├── sample_products.json  # 샘플 상품 데이터
└── requirements.txt
```

## 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# 터미널 1: 상점 서버 실행
python merchant_server.py

# 터미널 2: 클라이언트 데모 실행
python client_demo.py
```

## UCP Capabilities

이 데모에서 구현된 Capabilities:

| Capability | 설명 |
|------------|------|
| `discovery.product_search` | 상품 검색 |
| `discovery.product_details` | 상품 상세 조회 |
| `checkout.create_session` | 결제 세션 생성 |
| `checkout.submit_order` | 주문 제출 |

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
    │                                    │
    │ POST /ucp/checkout/submit          │
    │ ───────────────────────────────────>│  (4) 주문 제출
    │                                    │
    │        Order Confirmation          │
    │ <───────────────────────────────────│  (5) 주문 확인
```

## 참고

- 공식 저장소: https://github.com/Universal-Commerce-Protocol/samples
- 문서: https://ucp.dev/
