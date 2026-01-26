# x402 코드 플로우

## x402 공식 스펙 요약

> **출처**: [x402.org](https://www.x402.org/), [Coinbase x402 Docs](https://docs.cdp.coinbase.com/x402/welcome)

x402는 2025년 5월 Coinbase가 발표한 **HTTP 기반 결제 프로토콜**입니다. 오랫동안 사용되지 않던 HTTP 402 상태 코드를 활용하여 API와 디지털 콘텐츠에 대한 즉시 결제를 가능하게 합니다.

### 주요 파트너

- **인프라**: Cloudflare, Google Cloud, AWS
- **결제**: Coinbase, Circle, Visa, Stripe
- **AI**: Anthropic

### 핵심 특징

| 특징 | 설명 |
|------|------|
| **HTTP 네이티브** | 기존 HTTP 인프라 그대로 사용 |
| **계정 불필요** | 세션, 인증 없이 결제만으로 접근 |
| **AI 에이전트 친화적** | 프로그래밍 방식으로 자동 결제 |
| **스테이블코인** | USDC 기반 즉시 결제 (Base, Solana) |

### 채택 현황

> 2025년 런칭 후 6개월 만에 1억 건 이상의 결제 처리

---

## HTTP 402 상태 코드

### 역사

```
1997년: HTTP/1.1 스펙에 402 "Payment Required" 정의
        → "향후 사용을 위해 예약됨"
        → 28년간 미사용

2025년: Coinbase x402로 부활
        → AI 에이전트 시대에 맞는 마이크로페이먼트 표준
```

### 402 vs 다른 상태 코드

| 코드 | 의미 | 해결 방법 |
|------|------|----------|
| 401 | Unauthorized | 로그인 필요 |
| 403 | Forbidden | 권한 없음 |
| **402** | **Payment Required** | **결제 필요** |
| 404 | Not Found | 리소스 없음 |

---

## X-PAYMENT 헤더 상세

### 개요

X-PAYMENT는 x402의 핵심입니다. 클라이언트가 결제 정보를 서버에 전달하는 HTTP 헤더입니다.

```
GET /api/premium-data HTTP/1.1
Host: api.example.com
X-PAYMENT: eyJ2ZXJzaW9uIjoxLCJmcm9tIjoiMHgxMjM0Li4uIiwidG8iOi...
```

### X-PAYMENT 페이로드 구조

```json
{
  "version": 1,
  "from": "0xClientWallet1234...",
  "to": "0xServerWallet5678...",
  "amount": "100000",
  "asset": "USDC",
  "chain": "base",
  "nonce": "a1b2c3d4e5f6...",
  "deadline": 1706234400,
  "signature": "0x1234abcd..."
}
```

### 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| `version` | number | x402 프로토콜 버전 |
| `from` | string | 지불자 지갑 주소 |
| `to` | string | 수신자 지갑 주소 (서버) |
| `amount` | string | 결제 금액 (USDC는 6 decimals) |
| `asset` | string | 결제 자산 (USDC, USDT 등) |
| `chain` | string | 블록체인 네트워크 (base, solana) |
| `nonce` | string | 고유값 (이중 지불 방지) |
| `deadline` | number | 유효 기한 (Unix timestamp) |
| `signature` | string | EIP-712 서명 |

### 인코딩

X-PAYMENT 값은 **Base64 인코딩**됩니다:

```python
import json
import base64

payload = {"from": "0x...", "to": "0x...", "amount": "100000", ...}
x_payment = base64.b64encode(json.dumps(payload).encode()).decode()
# → "eyJ2ZXJzaW9uIjoxLCJmcm9tIjoi..."
```

---

## 전체 플로우

```
┌─────────────────┐                    ┌─────────────────┐
│     Client      │                    │   API Server    │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
    [1]  │  GET /api/premium-data               │
         │ ────────────────────────────────────▶│
         │                                      │
         │  402 Payment Required                │
         │  + accepts: [{payTo, amount, ...}]   │
         │ ◀────────────────────────────────────│
         │                                      │
    [2]  │  (결제 페이로드 생성 + 서명)            │
         │                                      │
    [3]  │  GET /api/premium-data               │
         │  X-PAYMENT: <base64 encoded>         │
         │ ────────────────────────────────────▶│
         │                                      │
         │  (서버: 결제 검증)                     │
         │  - 서명 확인                          │
         │  - 금액 확인                          │
         │  - nonce 중복 확인                    │
         │                                      │
         │  200 OK + 데이터                      │
         │  X-PAYMENT-RESPONSE: <결제 확인>      │
         │ ◀────────────────────────────────────│
         │                                      │
```

---

## 코드 매핑

### Step 1: 402 응답 수신

**client.py**
```python
def call_api(self, endpoint: str) -> dict:
    response = self.http.get(f"{API_URL}{endpoint}")

    if response.status_code == 402:
        # 결제 필요!
        return self._handle_402(url, response)
```

**server.py** (116-169줄)
```python
def create_402_response(resource: str):
    """402 Payment Required 응답 생성"""
    price = PRICES.get(resource, 100000)

    return Response(
        json.dumps({
            "error": "Payment Required",
            "accepts": [{
                "scheme": "exact",
                "network": "base",
                "asset": "USDC",
                "payTo": SERVER_WALLET,
                "maxAmountRequired": str(price),
                "resource": resource
            }],
            "x402Version": 1
        }),
        status=402,
        mimetype="application/json"
    )
```

### Step 2: 결제 페이로드 생성

**client.py**
```python
def _create_payment_payload(self, requirements: dict) -> dict:
    nonce = secrets.token_hex(16)
    deadline = int(time.time()) + 3600  # 1시간 유효

    payload = {
        "version": 1,
        "from": self.wallet_address,
        "to": requirements["payTo"],
        "amount": requirements["maxAmountRequired"],
        "asset": requirements["asset"],
        "chain": requirements["network"],
        "nonce": nonce,
        "deadline": deadline,
        "signature": self._sign_payment(requirements, nonce, deadline)
    }
    return payload


def _encode_payment_header(self, payload: dict) -> str:
    """Base64 인코딩"""
    json_str = json.dumps(payload)
    return base64.b64encode(json_str.encode()).decode()
```

### Step 3: X-PAYMENT 헤더와 함께 재요청

**client.py**
```python
def _handle_402(self, url: str, response: httpx.Response) -> dict:
    # 결제 요구사항 파싱
    payment_req = response.json()["accepts"][0]

    # 결제 페이로드 생성
    payment_payload = self._create_payment_payload(payment_req)
    payment_header = self._encode_payment_header(payment_payload)

    # X-PAYMENT 헤더와 함께 재요청
    response = self.http.get(url, headers={"X-PAYMENT": payment_header})

    if response.status_code == 200:
        return response.json()
```

**server.py** (54-88줄)
```python
@app.route("/api/premium-data", methods=["GET"])
def premium_data():
    payment_header = request.headers.get("X-PAYMENT")

    if not payment_header:
        return create_402_response("/api/premium-data")

    # 결제 검증
    is_valid, error = verify_payment(payment_header, "/api/premium-data")

    if not is_valid:
        return jsonify({"error": error}), 402

    # 결제 성공 - 데이터 반환
    return jsonify({"premium": True, "data": {...}})
```

### Step 4: 결제 검증

**server.py** (176-224줄)
```python
def verify_payment(payment_header: str, resource: str) -> tuple:
    # Base64 디코딩
    payload = json.loads(base64.b64decode(payment_header).decode())

    # 1. 수신 주소 확인
    if payload.get("to") != SERVER_WALLET:
        return False, "Invalid recipient address"

    # 2. 금액 확인
    required = PRICES.get(resource, 100000)
    paid = int(payload.get("amount", 0))
    if paid < required:
        return False, f"Insufficient payment: {paid} < {required}"

    # 3. nonce 중복 확인 (이중 지불 방지)
    nonce = payload.get("nonce")
    if nonce in USED_NONCES:
        return False, "Nonce already used"
    USED_NONCES.add(nonce)

    # 4. 서명 확인
    if not payload.get("signature"):
        return False, "Missing signature"

    return True, None
```

---

## 402 응답 구조

```json
{
  "error": "Payment Required",
  "accepts": [
    {
      "scheme": "exact",
      "network": "base",
      "asset": "USDC",
      "payTo": "0x742d35Cc6634C0532925a3b844Bc9e7595f1E2B4",
      "maxAmountRequired": "100000",
      "resource": "/api/premium-data",
      "description": "Access to /api/premium-data",
      "extra": {
        "name": "x402 Demo Server",
        "version": "1.0"
      }
    }
  ],
  "x402Version": 1
}
```

### accepts 필드 설명

| 필드 | 설명 |
|------|------|
| `scheme` | 결제 방식 (exact, range 등) |
| `network` | 블록체인 네트워크 |
| `asset` | 결제 자산 |
| `payTo` | 서버 지갑 주소 |
| `maxAmountRequired` | 필요 금액 (6 decimals) |
| `resource` | 결제 대상 리소스 |

---

## Nonce와 이중 지불 방지

### 문제: Replay Attack

```
공격자가 유효한 X-PAYMENT를 캡처
→ 같은 헤더로 반복 요청
→ 한 번 결제로 무한 사용?
```

### 해결: Nonce

```python
# 클라이언트: 매번 새로운 nonce 생성
nonce = secrets.token_hex(16)  # "a1b2c3d4e5f6..."

# 서버: 사용된 nonce 저장
USED_NONCES = set()

def verify_payment(payment_header):
    nonce = payload.get("nonce")

    if nonce in USED_NONCES:
        return False, "Nonce already used"  # 거부!

    USED_NONCES.add(nonce)  # 사용됨 표시
    return True, None
```

---

## Facilitator 역할 (미구현)

실제 x402에서는 **Facilitator**가 온체인 결제를 처리합니다.

```
┌────────┐    ┌────────┐    ┌─────────────┐    ┌──────────┐
│ Client │───▶│ Server │───▶│ Facilitator │───▶│ Blockchain│
└────────┘    └────────┘    └─────────────┘    └──────────┘
                                   │
                            Coinbase CDP
                            (fee-free USDC)
```

### Facilitator의 역할

1. **서명 검증**: EIP-712 서명 확인
2. **온체인 검증**: 잔액 확인, 트랜잭션 실행
3. **결제 정산**: USDC 전송

### Coinbase Facilitator

```python
# 실제 구현 예시 (미구현)
def verify_with_facilitator(payment_header: str) -> bool:
    response = httpx.post(
        "https://api.cdp.coinbase.com/x402/verify",
        headers={"Authorization": f"Bearer {CDP_API_KEY}"},
        json={"payment": payment_header}
    )
    return response.json().get("valid", False)
```

---

## x402의 특징: Stateless

### Stateless란?

x402는 **완전한 Stateless** 프로토콜입니다. 서버는 클라이언트의 이전 요청을 기억하지 않습니다.

```
A2A + AP2, UCP (Stateful)          x402 (Stateless)
─────────────────────────          ─────────────────────
Task/Session 생성                  요청마다 독립적
      ↓                                  │
상태 유지 (pending → completed)          │
      ↓                                  │
여러 단계에 걸친 거래                 단일 요청 = 단일 결제
```

### Stateless의 장점

| 장점 | 설명 |
|------|------|
| **단순함** | 세션 관리 불필요, 구현이 쉬움 |
| **확장성** | 서버가 상태를 저장하지 않아 수평 확장 용이 |
| **독립성** | 각 요청이 완전히 독립적, 장애 전파 없음 |
| **캐싱** | HTTP 캐싱 인프라 그대로 활용 가능 |

### Stateless의 약점 (x402의 한계)

| 약점 | 설명 | 대안 |
|------|------|------|
| **장바구니 불가** | 여러 상품을 모아서 한 번에 결제 불가 | UCP 사용 |
| **환불 어려움** | 거래 기록이 없어 환불 처리 복잡 | 별도 환불 시스템 필요 |
| **구독 불가** | 반복 결제를 위한 상태 저장 불가 | 별도 구독 시스템 필요 |
| **주문 추적 불가** | 배송 상태 등 추적 불가 | UCP/A2A 사용 |
| **고객 관계 없음** | 로열티 프로그램, 개인화 불가 | 별도 계정 시스템 필요 |
| **부분 결제 불가** | 할부, 분할 결제 불가 | UCP 사용 |

### 비유: 자판기 vs 쇼핑몰

```
x402 = 자판기
────────────────
동전 넣고 → 음료 나옴
끝. 자판기는 당신을 기억하지 않음.

UCP = 쇼핑몰
────────────────
로그인 → 장바구니 담기 → 결제 → 배송 추적
쇼핑몰은 당신의 구매 내역을 기억함.
```

### 언제 Stateless가 적합한가?

```
✓ API 호출당 과금 (GPT API, 이미지 생성 등)
✓ 콘텐츠 단건 구매 (기사, 영상)
✓ 일회성 서비스 (번역, 요약)
✓ AI 에이전트 자동 결제 (도구 사용료)

✗ 이커머스 (장바구니, 배송)
✗ 구독 서비스 (SaaS, 멤버십)
✗ 고객 관계 관리 (포인트, 등급)
```

---

## A2A+AP2 vs UCP vs x402 비교

| | A2A + AP2 | UCP | x402 |
|---|-----------|-----|------|
| **발표** | Google | Google | Coinbase |
| **복잡도** | 높음 | 중간 | **낮음** |
| **통신** | JSON-RPC | REST | HTTP 상태코드 |
| **결제** | Mandate 시스템 | Checkout Session | **X-PAYMENT 헤더** |
| **용도** | 에이전트 간 거래 | 범용 상거래 | **마이크로페이먼트** |
| **인증** | Agent Card | Capability Profile | 불필요 |

### 언제 x402를 사용하나?

```
✓ API 호출당 과금
✓ 콘텐츠 페이월
✓ AI 에이전트 자동 결제
✓ 계정/세션 없는 결제

✗ 복잡한 장바구니
✗ 배송이 필요한 물리적 상품
✗ 구독 서비스
```

---

## 현재 구현의 한계 (데모용 단순화)

| 공식 스펙 | 현재 구현 |
|----------|----------|
| EIP-712 서명 검증 | SHA256 해시 (시뮬레이션) |
| Facilitator 온체인 처리 | 로컬 검증만 |
| 실제 USDC 전송 | 시뮬레이션 |
| X-PAYMENT-RESPONSE 헤더 | 미구현 |

이 데모는 학습 목적으로 핵심 플로우를 이해하기 위해 단순화되었습니다.

---

## 참고 자료

- [x402.org - Official Site](https://www.x402.org/)
- [Coinbase x402 Documentation](https://docs.cdp.coinbase.com/x402/welcome)
- [GitHub - coinbase/x402](https://github.com/coinbase/x402)
- [Cloudflare x402 Integration](https://blog.cloudflare.com/x402/)
- [x402 V2 Launch Announcement](https://www.x402.org/writing/x402-v2-launch)
