# x402 프로토콜 학습 가이드

> HTTP 402 상태 코드를 활용한 네이티브 웹 결제 프로토콜

## 한 줄 요약

**x402는 "돈이 필요한 API"를 만드는 프로토콜이다.** 서버가 402를 반환하면, 클라이언트가 자동으로 결제하고 다시 요청한다.

---

## 1. 왜 x402인가?

HTTP에는 원래 **402 Payment Required** 상태 코드가 있었지만, 실제로 쓰이지 않았다. 온라인 결제가 카드사/PG를 거치는 복잡한 과정이었기 때문.

블록체인이 이걸 바꿨다:
- **즉시 결제**: 블록체인 전송은 몇 초면 끝남
- **프로그래밍 가능**: 지갑이 API 클라이언트에 내장 가능
- **수수료 최소화**: USDC 같은 스테이블코인으로 $0.001 단위 결제 가능

x402는 이 기회를 활용해 **HTTP 자체에 결제를 내장**한다.

---

## 2. 핵심 흐름 (3단계)

```
클라이언트                    서버                    Facilitator
   │                          │                          │
   │── GET /api/data ────────>│                          │
   │                          │                          │
   │<── 402 Payment Required ─│                          │
   │    PAYMENT-REQUIRED 헤더  │                          │
   │    (얼마, 어디로, 어떤 토큰)                          │
   │                          │                          │
   │   [지갑으로 결제 서명]     │                          │
   │                          │                          │
   │── GET /api/data ────────>│                          │
   │   PAYMENT-SIGNATURE 헤더  │                          │
   │                          │── POST /verify ─────────>│
   │                          │<── { isValid: true } ────│
   │                          │                          │
   │<── 200 OK ───────────────│                          │
   │    PAYMENT-RESPONSE 헤더  │                          │
   │    + 실제 데이터           │── POST /settle ─────────>│
   │                          │<── { transaction: 0x.. } ─│
```

### Step 1: 서버가 "돈 내라" (402)
```
HTTP/1.1 402 Payment Required
PAYMENT-REQUIRED: <Base64 JSON>
```

### Step 2: 클라이언트가 "여기 돈" (서명)
```
GET /api/data
PAYMENT-SIGNATURE: <Base64 JSON>
```

### Step 3: 서버가 "확인됨, 여기 데이터" (200)
```
HTTP/1.1 200 OK
PAYMENT-RESPONSE: <Base64 JSON>
Body: { actual data }
```

---

## 3. V2 헤더 상세 구조

### 3.1 PAYMENT-REQUIRED (서버 → 클라이언트)

402 응답에 포함. "이만큼 내면 데이터 줄게."

```json
{
  "x402Version": 2,
  "resource": {
    "url": "/api/data",
    "description": "Premium weather data",
    "mimeType": "application/json"
  },
  "accepts": [
    {
      "scheme": "exact",
      "network": "eip155:84532",
      "amount": "100000",
      "asset": "0x036CbD...CF7e",
      "payTo": "0x742d...bD18",
      "maxTimeoutSeconds": 3600,
      "extra": { "name": "USDC", "version": "2" }
    }
  ]
}
```

| 필드 | 설명 |
|------|------|
| `x402Version` | 프로토콜 버전. 현재 `2` |
| `resource` | 결제 대상 리소스 정보 |
| `accepts[]` | 서버가 받아들이는 결제 옵션 (복수 가능) |
| `scheme` | 결제 스킴. `"exact"` = 정확한 금액 |
| `network` | 블록체인 네트워크 (CAIP-2 형식) |
| `amount` | 금액 (토큰의 최소 단위). USDC 6 decimals → `"100000"` = $0.10 |
| `asset` | 토큰 컨트랙트 주소 |
| `payTo` | 수신 지갑 주소 |

### 3.2 PAYMENT-SIGNATURE (클라이언트 → 서버)

재요청에 포함. "이 서명으로 결제합니다."

```json
{
  "x402Version": 2,
  "accepted": {
    "scheme": "exact",
    "network": "eip155:84532",
    "amount": "100000",
    "asset": "0x036CbD...CF7e",
    "payTo": "0x742d...bD18"
  },
  "payload": {
    "signature": "0x...(EIP-712 서명)",
    "authorization": {
      "from": "0xPayer...",
      "to": "0x742d...bD18",
      "value": "100000",
      "validAfter": 0,
      "validBefore": 1742169600,
      "nonce": "0x..."
    }
  }
}
```

| 필드 | 설명 |
|------|------|
| `accepted` | 서버의 `accepts[]` 중 선택한 옵션 (그대로 복사) |
| `payload.signature` | EIP-712 typed data 서명 (Permit2) |
| `payload.authorization` | USDC Transfer Authorization 세부 정보 |

### 3.3 PAYMENT-RESPONSE (서버 → 클라이언트)

200 응답에 포함. "결제 완료, 여기 영수증."

```json
{
  "success": true,
  "transaction": "0x9f8e...(블록체인 tx hash)",
  "network": "eip155:84532",
  "payer": "0xPayer..."
}
```

| 필드 | 설명 |
|------|------|
| `success` | 결제 성공 여부 |
| `transaction` | 온체인 트랜잭션 해시 |
| `network` | 결제된 네트워크 |
| `payer` | 결제한 지갑 주소 |

---

## 4. Facilitator란?

서버가 직접 블록체인을 검증하기 어려우므로, **Facilitator**가 대행한다.

```
서버 ──> Facilitator: "이 결제 맞아?"
         Facilitator: "네, 유효합니다"  (verify)
서버 ──> Facilitator: "온체인으로 정산해줘"
         Facilitator: "완료. tx: 0x..."  (settle)
```

### 사용 가능한 Facilitator

| 이름 | URL | 인증 | 비용 |
|------|-----|------|------|
| x402.org (테스트넷) | `https://x402.org/facilitator` | 불필요 | 무료 |
| Coinbase CDP | `https://api.cdp.coinbase.com/platform/v2/x402` | CDP API Key | 1,000건/월 무료 |

### API 엔드포인트

**POST /verify** — 서명 검증 (온체인 없음, 빠름)
```json
// 요청
{ "x402Version": 2, "paymentPayload": {...}, "paymentRequirements": {...} }
// 응답
{ "isValid": true, "payer": "0x..." }
```

**POST /settle** — 온체인 정산 (블록체인 트랜잭션 발생)
```json
// 요청
{ "x402Version": 2, "paymentPayload": {...}, "paymentRequirements": {...} }
// 응답
{ "success": true, "transaction": "0x...", "network": "eip155:84532", "payer": "0x..." }
```

---

## 5. V1 vs V2 차이점

| 항목 | V1 | V2 |
|------|----|----|
| 결제 요구사항 위치 | 응답 **Body** | `PAYMENT-REQUIRED` **헤더** |
| 결제 서명 헤더 | `X-PAYMENT` | `PAYMENT-SIGNATURE` |
| 정산 결과 헤더 | `X-PAYMENT-RESPONSE` | `PAYMENT-RESPONSE` |
| 금액 필드명 | `maxAmountRequired` | `amount` |
| 네트워크 형식 | `"base-sepolia"` | `"eip155:84532"` (CAIP-2) |
| PaymentPayload 구조 | `{ scheme, network, payload }` (플랫) | `{ accepted: {...}, payload }` (중첩) |
| 리소스 정보 | accepts 안에 포함 | 최상위 `resource` 객체로 분리 |

---

## 6. 네트워크 ID (CAIP-2)

V2는 [CAIP-2](https://github.com/ChainAgnostic/CAIPs/blob/main/CAIPs/caip-2.md) 형식으로 네트워크를 표기한다:

| 네트워크 | CAIP-2 ID |
|----------|-----------|
| Base Mainnet | `eip155:8453` |
| Base Sepolia (테스트넷) | `eip155:84532` |
| Ethereum Mainnet | `eip155:1` |
| Polygon | `eip155:137` |
| Solana Mainnet | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` |
| Solana Devnet | `solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1` |

---

## 7. 실제 구현 방법

### Python 서버 (실제 SDK 사용)

```bash
pip install "x402[fastapi,evm]"
```

```python
from fastapi import FastAPI
from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
from x402.http.middleware.fastapi import PaymentMiddlewareASGI
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.server import x402ResourceServer

app = FastAPI()

server = x402ResourceServer(
    HTTPFacilitatorClient(FacilitatorConfig(url="https://x402.org/facilitator"))
)
server.register("eip155:84532", ExactEvmServerScheme())

routes = {
    "GET /api/data": RouteConfig(
        accepts=[PaymentOption(scheme="exact", pay_to="0xYOUR_ADDR", price="$0.10", network="eip155:84532")],
        description="Paid API",
    ),
}
# 이 한 줄이 402 응답 + 결제 검증을 자동 처리
app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=server)

@app.get("/api/data")
async def get_data():
    return {"result": "paid content"}  # 결제 완료된 요청만 여기 도달
```

### Python 클라이언트 (자동 결제)

```bash
pip install "x402[httpx,evm]"
```

```python
from eth_account import Account
from x402 import x402Client
from x402.http.clients import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client

client = x402Client()
account = Account.from_key("0xYOUR_PRIVATE_KEY")
register_exact_evm_client(client, EthAccountSigner(account))

# 402를 받으면 자동으로 서명하고 재요청
async with x402HttpxClient(client) as http:
    response = await http.get("http://server:4021/api/data")
    print(response.json())  # {"result": "paid content"}
```

---

## 8. 이 프로젝트의 시뮬레이션

이 프로젝트(Agent M Soul Store)는 x402 V2 프로토콜 흐름을 **정확히 따르되**, 블록체인 부분만 시뮬레이션한다:

| 구성 요소 | 실제 구현 | 시뮬레이션 |
|-----------|:--------:|:---------:|
| HTTP 402 응답 | O | |
| PAYMENT-REQUIRED 헤더 (V2) | O | |
| PAYMENT-SIGNATURE 헤더 (V2) | O | |
| PAYMENT-RESPONSE 헤더 (V2) | O | |
| Base64 인코딩 | O | |
| EIP-712 서명 | | SHA256 해시 |
| Facilitator verify/settle | | 로컬 검증 |
| 온체인 USDC 전송 | | 생략 |
| 지갑 연결 (MetaMask) | | 랜덤 주소 |

프로토콜 흐름과 데이터 구조는 실제와 동일하므로, 실제 x402 SDK로 교체 시 서버/클라이언트 코드만 바꾸면 된다.

---

## 참고 자료

- [coinbase/x402 GitHub](https://github.com/coinbase/x402) — 공식 모노레포 (모든 SDK)
- [x402 V2 Specification](https://github.com/coinbase/x402/blob/main/specs/x402-specification-v2.md)
- [x402 V2 HTTP Transport](https://github.com/coinbase/x402/blob/main/specs/transports-v2/http.md)
- [Coinbase x402 Documentation](https://docs.cdp.coinbase.com/x402/)
- [x402.org](https://www.x402.org/) — 프로토콜 공식 사이트
- [x402 Python SDK (PyPI)](https://pypi.org/project/x402/)
