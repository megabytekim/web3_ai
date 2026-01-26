# x402 프로토콜 데모

## 개요

이 데모는 **x402 프로토콜**의 핵심 개념을 보여줍니다.

x402는 2025년 5월 Coinbase가 발표한 HTTP 기반 결제 프로토콜로, 오랫동안 미사용이던 HTTP 402 상태 코드를 활용합니다. Cloudflare, Visa, Anthropic 등이 파트너로 참여하고 있습니다.

### 핵심 개념

1. **402 Payment Required**: 결제가 필요한 리소스에 대한 HTTP 응답
2. **X-PAYMENT Header**: 결제 정보를 담은 HTTP 헤더 (Base64 인코딩)
3. **Nonce**: 이중 지불 방지를 위한 고유값
4. **Facilitator**: 온체인 결제 검증 및 정산 서비스

### 3가지 프로토콜 비교

| | A2A + AP2 | UCP | x402 |
|---|-----------|-----|------|
| 복잡도 | 높음 | 중간 | **낮음** |
| 통신 | JSON-RPC | REST | HTTP 상태코드 |
| 결제 | Mandate | Checkout Session | X-PAYMENT 헤더 |
| 용도 | 에이전트 간 거래 | 범용 상거래 | 마이크로페이먼트 |

## 파일 구조

```
x402/
├── server.py               # 402 응답을 반환하는 유료 API 서버
├── client.py               # X-PAYMENT 헤더로 결제하는 클라이언트
├── code_flow.md            # 상세 플로우 문서
├── test_x402_unit.py       # 단위 테스트
├── test_x402_integration.py # 통합 테스트
└── requirements.txt
```

## 실행 방법

```bash
# 가상환경 활성화 (week-6 루트에서)
source ../venv/bin/activate

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
    │         + accepts: [{payTo, ...}]   │
    │ <───────────────────────────────────│  (1) 결제 요구사항
    │                                     │
    │ [결제 페이로드 생성 + 서명]            │
    │                                     │
    │ GET /api/premium-data               │
    │ X-PAYMENT: <base64 encoded>         │
    │ ───────────────────────────────────>│  (2) 결제 헤더 포함
    │                                     │
    │         200 OK + Data               │
    │ <───────────────────────────────────│  (3) 데이터 반환
```

## 출력 예시

```
=== x402 데모: 결제 클라이언트 ===

[테스트 1] 무료 API 호출
  ✓ 성공 (무료)

[테스트 2] 유료 API 호출 ($0.10)
  ⚠ 402 Payment Required
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

## 테스트 실행

```bash
# 단위 테스트
pytest test_x402_unit.py -v

# 통합 테스트
pytest test_x402_integration.py -v

# 전체 테스트
pytest -v
```

## X-PAYMENT 헤더

### 구조

```json
{
  "version": 1,
  "from": "0xClientWallet...",
  "to": "0xServerWallet...",
  "amount": "100000",
  "asset": "USDC",
  "chain": "base",
  "nonce": "a1b2c3d4...",
  "deadline": 1706234567,
  "signature": "0x..."
}
```

### 인코딩

```python
import base64, json
x_payment = base64.b64encode(json.dumps(payload).encode()).decode()
```

## 현재 구현의 한계 (데모용 단순화)

| 공식 스펙 | 현재 구현 |
|----------|----------|
| EIP-712 서명 검증 | SHA256 해시 (시뮬레이션) |
| Facilitator 온체인 처리 | 로컬 검증만 |
| 실제 USDC 전송 | 시뮬레이션 |

자세한 플로우 설명은 [code_flow.md](./code_flow.md)를 참고하세요.

## 참고

- [x402.org - Official Site](https://www.x402.org/)
- [Coinbase x402 Documentation](https://docs.cdp.coinbase.com/x402/welcome)
- [GitHub - coinbase/x402](https://github.com/coinbase/x402)
- [Cloudflare x402 Integration](https://blog.cloudflare.com/x402/)
