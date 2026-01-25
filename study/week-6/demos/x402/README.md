# x402 프로토콜 데모

## 개요

이 데모는 **x402 프로토콜**의 핵심 개념을 보여줍니다.
x402는 HTTP 402 (Payment Required) 상태 코드를 활용한 인터넷 네이티브 결제 프로토콜입니다.

### 핵심 개념

1. **402 Payment Required**: 결제가 필요한 리소스에 대한 HTTP 응답
2. **Payment Requirements**: 결제 조건 (수신 주소, 금액, 네트워크 등)
3. **X-PAYMENT Header**: 결제 정보를 담은 HTTP 헤더
4. **Facilitator**: 결제 검증 및 정산 서비스

## 파일 구조

```
x402/
├── server.py        # 402 응답을 반환하는 유료 API 서버
├── client.py        # X-PAYMENT 헤더로 결제하는 클라이언트
└── requirements.txt
```

## 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# 터미널 1: 유료 API 서버 실행
python server.py

# 터미널 2: 클라이언트 실행
python client.py
```

## x402 플로우

```
[Client]                           [Paid API Server]
    │                                     │
    │ GET /api/premium-data               │
    │ ───────────────────────────────────>│
    │                                     │
    │         402 Payment Required        │
    │ <───────────────────────────────────│  (1) 결제 요구사항 반환
    │                                     │
    │ [결제 페이로드 생성 및 서명]           │
    │                                     │
    │ GET /api/premium-data               │
    │ X-PAYMENT: <payment_payload>        │
    │ ───────────────────────────────────>│  (2) 결제 헤더와 함께 재요청
    │                                     │
    │         200 OK + Data               │
    │ <───────────────────────────────────│  (3) 데이터 반환
```

## 402 응답 예시

```json
{
  "error": "Payment Required",
  "accepts": [
    {
      "scheme": "exact",
      "network": "base",
      "asset": "USDC",
      "payTo": "0x1234...5678",
      "maxAmountRequired": "100000",
      "resource": "/api/premium-data",
      "description": "Premium API access"
    }
  ]
}
```

## X-PAYMENT 헤더 예시

```json
{
  "version": 1,
  "from": "0xClientWallet...",
  "to": "0xServerWallet...",
  "amount": "100000",
  "asset": "USDC",
  "chain": "base",
  "nonce": "abc123",
  "deadline": 1706234567,
  "signature": "0x..."
}
```

## 참고

- 공식 저장소: https://github.com/coinbase/x402 (4.3k stars)
- 문서: https://docs.cdp.coinbase.com/x402/welcome
- 데모: https://x402.org
