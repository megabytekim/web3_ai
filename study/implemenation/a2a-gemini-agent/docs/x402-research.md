# x402 Protocol -- 실제 구현 라이브러리 리서치

> 조사일: 2026-03-16
> x402 Python SDK 최신 버전: 2.3.0 (2026-03-06)
> x402 TypeScript @x402/paywall 최신 버전: 2.6.0 (2026-03-14)

---

## 1. 공식 SDK/라이브러리 현황

### 1.1 Python (PyPI)

**패키지명**: `x402`
**라이선스**: MIT
**저자**: Coinbase
**Python**: >= 3.10

```bash
# HTTP 클라이언트 (택 1)
pip install "x402[httpx]"       # async (권장)
pip install "x402[requests]"    # sync

# 서버 프레임워크 (택 1)
pip install "x402[fastapi]"     # FastAPI/Starlette ASGI 미들웨어
pip install "x402[flask]"       # Flask WSGI 미들웨어

# 블록체인 메커니즘 (택 1 이상)
pip install "x402[evm]"         # EVM/Ethereum (Base, Polygon 등)
pip install "x402[svm]"         # Solana

# 전체 설치
pip install "x402[all]"

# 조합 설치 예시
pip install "x402[fastapi,httpx,evm]"
```

**핵심 모듈 구조**:
| 모듈 | 역할 |
|------|------|
| `x402.client` | `x402Client` (async), `x402ClientSync` (sync) |
| `x402.server` | `x402ResourceServer` (async), `x402ResourceServerSync` (sync) |
| `x402.facilitator` | `x402Facilitator` (async), `x402FacilitatorSync` (sync) |
| `x402.http` | HTTP 클라이언트, 미들웨어, Facilitator 클라이언트 |
| `x402.http.middleware.fastapi` | `PaymentMiddlewareASGI`, `payment_middleware` |
| `x402.http.middleware.flask` | `payment_middleware` |
| `x402.http.clients` | `x402HttpxClient`, `x402RequestsClient` |
| `x402.mechanisms.evm.exact` | `ExactEvmScheme`, `ExactEvmServerScheme`, `ExactEvmFacilitatorScheme` |
| `x402.mechanisms.svm.exact` | `ExactSvmScheme`, `ExactSvmServerScheme`, `ExactSvmFacilitatorScheme` |
| `x402.schemas` | `AssetAmount`, `Network` 등 데이터 모델 |
| `x402.extensions` | Bazaar discovery 등 프로토콜 확장 |

### 1.2 TypeScript/Node.js (npm)

**V2 패키지 (현행, @x402 스코프)**:
```bash
# 코어
npm install @x402/core @x402/evm @x402/svm

# 서버 미들웨어 (택 1)
npm install @x402/express
npm install @x402/hono
npm install @x402/next

# 클라이언트 (택 1)
npm install @x402/fetch
npm install @x402/axios

# UI / 확장
npm install @x402/paywall
npm install @x402/extensions
```

**Coinbase Facilitator 전용 패키지**:
```bash
npm install @coinbase/x402
```

**V1 레거시 패키지 (deprecated, 스코프 없음)**:
```bash
npm install x402-express    # 아직 동작하지만 V1 헤더 사용
npm install x402-next
npm install x402-hono
```

### 1.3 Go

```bash
go get github.com/coinbase/x402/go
```

### 1.4 Java

```
// coinbase/x402 리포지토리의 java/ 디렉토리 참조
```

### 1.5 기타 커뮤니티 구현

| 언어/플랫폼 | 리포지토리 | 설명 |
|-------------|-----------|------|
| Rust | `x402-rs/x402-rs` | verify, settle, monitor 지원 |
| .NET | `michielpost/x402-dotnet` | Solana 포함, ASP.NET 미들웨어 |
| Go (MCP) | `mark3labs/mcp-go-x402` | MCP 서버/클라이언트용 x402 transport |
| A2A+x402 | `google-agentic-commerce/a2a-x402` | A2A 프로토콜에 x402 결제 통합 |

---

## 2. GitHub 공식 리포지토리 구조

**리포지토리**: https://github.com/coinbase/x402
**스타**: 5.7k+ / **컨트리뷰터**: 245명 / **라이선스**: Apache 2.0

```
coinbase/x402/
  contracts/evm/          # EVM 스마트 컨트랙트 (Permit2 등)
  docs/                   # GitBook 문서 소스
  specs/                  # 프로토콜 명세서
  go/                     # Go SDK
  python/
    legacy/               # V1 Python 코드
    x402/                 # V2 Python SDK (PyPI 배포 소스)
  typescript/
    packages/
      @x402/core/
      @x402/evm/
      @x402/svm/
      @x402/express/
      @x402/fetch/
      @x402/axios/
      @x402/hono/
      @x402/next/
      @x402/paywall/
      @x402/extensions/
  java/                   # Java SDK
  examples/
    python/
      servers/
        fastapi/          # FastAPI 서버 예제
        flask/            # Flask 서버 예제
        advanced/         # 고급 설정 예제
        custom/           # 커스텀 구현
        mcp/              # MCP 서버 예제
        payment-identifier/
      clients/
        httpx/            # async 클라이언트 예제
        requests/         # sync 클라이언트 예제
    typescript/
      servers/
        express/
        hono/
        next/
      clients/
  e2e/                    # End-to-end 테스트
```

---

## 3. 서버 사이드 구현: 402 응답 + 결제 검증

### 3.1 프로토콜 플로우 (V2)

```
Client                    Resource Server              Facilitator
  |                            |                           |
  |--- GET /weather ---------->|                           |
  |                            |                           |
  |<-- 402 Payment Required ---|                           |
  |    Header: PAYMENT-REQUIRED (base64 JSON)              |
  |                            |                           |
  |--- GET /weather ---------->|                           |
  |    Header: PAYMENT-SIGNATURE (base64 signed payload)   |
  |                            |                           |
  |                            |--- POST /verify --------->|
  |                            |<-- { is_valid: true } ----|
  |                            |                           |
  |<-- 200 OK ----------------|                           |
  |    Header: PAYMENT-RESPONSE                            |
  |    Body: { weather data }  |                           |
  |                            |                           |
  |                            |--- POST /settle --------->|
  |                            |<-- { tx_hash: "0x..." } --|
```

### 3.2 HTTP 헤더 명세 (V2 vs V1)

| 목적 | V2 (현행) | V1 (레거시) |
|------|-----------|-------------|
| 결제 요구사항 (서버 -> 클라이언트) | `PAYMENT-REQUIRED` | 응답 Body에 JSON |
| 결제 서명 (클라이언트 -> 서버) | `PAYMENT-SIGNATURE` | `X-PAYMENT` |
| 정산 결과 (서버 -> 클라이언트) | `PAYMENT-RESPONSE` | `X-PAYMENT-RESPONSE` |

> V2는 V1과 하위 호환됨. SDK가 두 버전 모두 처리.

### 3.3 Python/FastAPI 서버 구현 (공식 예제)

```python
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
from x402.http.middleware.fastapi import PaymentMiddlewareASGI
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.mechanisms.svm.exact import ExactSvmServerScheme
from x402.schemas import AssetAmount, Network
from x402.server import x402ResourceServer

load_dotenv()

# --- 설정 ---
EVM_ADDRESS = os.getenv("EVM_ADDRESS")                   # 수신 지갑 주소
SVM_ADDRESS = os.getenv("SVM_ADDRESS")                   # Solana 수신 주소
EVM_NETWORK: Network = "eip155:84532"                     # Base Sepolia (테스트넷)
SVM_NETWORK: Network = "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1"  # Solana Devnet
FACILITATOR_URL = os.getenv("FACILITATOR_URL", "https://x402.org/facilitator")

# --- 응답 스키마 ---
class WeatherReport(BaseModel):
    weather: str
    temperature: int

class WeatherResponse(BaseModel):
    report: WeatherReport

class PremiumContentResponse(BaseModel):
    content: str

# --- FastAPI 앱 ---
app = FastAPI()

# --- x402 리소스 서버 초기화 ---
facilitator = HTTPFacilitatorClient(FacilitatorConfig(url=FACILITATOR_URL))
server = x402ResourceServer(facilitator)
server.register(EVM_NETWORK, ExactEvmServerScheme())
server.register(SVM_NETWORK, ExactSvmServerScheme())

# --- 결제 보호 라우트 정의 ---
routes = {
    "GET /weather": RouteConfig(
        accepts=[
            PaymentOption(
                scheme="exact",
                pay_to=EVM_ADDRESS,
                price="$0.01",                            # USD 표기
                network=EVM_NETWORK,
            ),
            PaymentOption(
                scheme="exact",
                pay_to=SVM_ADDRESS,
                price="$0.01",
                network=SVM_NETWORK,
            ),
        ],
        mime_type="application/json",
        description="Weather report",
    ),
    "GET /premium/*": RouteConfig(                        # 와일드카드 매칭
        accepts=[
            PaymentOption(
                scheme="exact",
                pay_to=EVM_ADDRESS,
                price=AssetAmount(                        # 토큰 직접 지정
                    amount="10000",                       # $0.01 USDC (6 decimals)
                    asset="0x036CbD53842c5426634e7929541eC2318f3dCF7e",
                    extra={"name": "USDC", "version": "2"},
                ),
                network=EVM_NETWORK,
            ),
            PaymentOption(
                scheme="exact",
                pay_to=SVM_ADDRESS,
                price="$0.01",
                network=SVM_NETWORK,
            ),
        ],
        mime_type="application/json",
        description="Premium content",
    ),
}

# --- 미들웨어 등록 (핵심: 이 한 줄이 402 응답 + 검증을 처리) ---
app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=server)

# --- 라우트 핸들러 ---
@app.get("/health")                                      # 결제 불필요
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/weather")                                     # 결제 필요: $0.01
async def get_weather() -> WeatherResponse:
    return WeatherResponse(report=WeatherReport(weather="sunny", temperature=70))

@app.get("/premium/content")                             # 결제 필요: $0.01
async def get_premium_content() -> PremiumContentResponse:
    return PremiumContentResponse(content="This is premium content")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4021)
```

**미들웨어가 자동으로 처리하는 것**:
1. `routes`에 정의되지 않은 경로 -> 그대로 통과 (예: `/health`)
2. `routes`에 정의된 경로 + `PAYMENT-SIGNATURE` 헤더 없음 -> `402 Payment Required` + `PAYMENT-REQUIRED` 헤더
3. `routes`에 정의된 경로 + `PAYMENT-SIGNATURE` 헤더 있음 -> Facilitator에 검증 요청 -> 성공 시 핸들러 실행

### 3.4 Python/Flask 서버 구현 (공식 예제)

```python
import os
from dotenv import load_dotenv
from flask import Flask, jsonify

from x402.http import FacilitatorConfig, HTTPFacilitatorClientSync, PaymentOption
from x402.http.middleware.flask import payment_middleware
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.mechanisms.svm.exact import ExactSvmServerScheme
from x402.schemas import AssetAmount, Network
from x402.server import x402ResourceServerSync

load_dotenv()

EVM_ADDRESS = os.getenv("EVM_ADDRESS")
SVM_ADDRESS = os.getenv("SVM_ADDRESS")
EVM_NETWORK: Network = "eip155:84532"
SVM_NETWORK: Network = "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1"
FACILITATOR_URL = os.getenv("FACILITATOR_URL", "https://x402.org/facilitator")

app = Flask(__name__)

# Sync 버전 사용 (Flask는 WSGI)
facilitator = HTTPFacilitatorClientSync(FacilitatorConfig(url=FACILITATOR_URL))
server = x402ResourceServerSync(facilitator)
server.register(EVM_NETWORK, ExactEvmServerScheme())
server.register(SVM_NETWORK, ExactSvmServerScheme())

routes = {
    "GET /weather": RouteConfig(
        accepts=[
            PaymentOption(scheme="exact", pay_to=EVM_ADDRESS, price="$0.01", network=EVM_NETWORK),
            PaymentOption(scheme="exact", pay_to=SVM_ADDRESS, price="$0.01", network=SVM_NETWORK),
        ],
        mime_type="application/json",
        description="Weather report",
    ),
}
# Flask에서는 함수 호출 방식
payment_middleware(app, routes=routes, server=server)

@app.route("/health")
def health_check():
    return jsonify({"status": "ok"})

@app.route("/weather")
def get_weather():
    return jsonify({"report": {"weather": "sunny", "temperature": 70}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4021, debug=False)
```

### 3.5 TypeScript/Express 서버 구현

```typescript
import express from "express";
import { paymentMiddleware } from "@x402/express";  // 또는 "x402-express" (V1)
import dotenv from "dotenv";

dotenv.config();
const app = express();

const network = "base-sepolia";
const facilitatorObj = { url: "https://x402.org/facilitator" };

// 미들웨어 한 줄로 결제 보호
app.use(
  paymentMiddleware(
    process.env.WALLET_ADDRESS,   // 수신 지갑 주소
    {
      "GET /weather": {
        price: "$0.10",
        network: network,
        config: {
          description: "Weather data API",
        },
      },
      "GET /premium/*": {
        price: {
          amount: "100000",
          asset: {
            address: "0xabc...",
            decimals: 18,
            eip712: { name: "WETH", version: "1" },
          },
        },
        network: network,
      },
    },
    facilitatorObj,
  ),
);

app.get("/weather", (req, res) => {
  res.json({ weather: "sunny", temperature: 70 });
});

app.get("/premium/content", (req, res) => {
  res.json({ content: "Premium content" });
});

app.listen(4021, () => console.log("Server running on :4021"));
```

---

## 4. Python 클라이언트 구현 (결제 자동 처리)

### 4.1 httpx async 클라이언트 (공식 예제)

```python
import asyncio
import os
from dotenv import load_dotenv
from eth_account import Account

from x402 import x402Client
from x402.http import x402HTTPClient
from x402.http.clients import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client
from x402.mechanisms.svm import KeypairSigner
from x402.mechanisms.svm.exact.register import register_exact_svm_client

load_dotenv()

async def main():
    evm_private_key = os.getenv("EVM_PRIVATE_KEY")
    base_url = os.getenv("RESOURCE_SERVER_URL")    # e.g. "http://localhost:4021"
    endpoint_path = os.getenv("ENDPOINT_PATH")     # e.g. "/weather"

    # x402 클라이언트 생성
    client = x402Client()

    # EVM 결제 메커니즘 등록
    if evm_private_key:
        account = Account.from_key(evm_private_key)
        register_exact_evm_client(client, EthAccountSigner(account))
        print(f"EVM account: {account.address}")

    # HTTP 헬퍼
    http_client = x402HTTPClient(client)
    url = f"{base_url}{endpoint_path}"

    # 자동 결제 처리 HTTP 클라이언트
    async with x402HttpxClient(client) as http:
        response = await http.get(url)
        await response.aread()

        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")

        # 정산 응답 확인
        try:
            settle_response = http_client.get_payment_settle_response(
                lambda name: response.headers.get(name)
            )
            print(f"Payment response: {settle_response.model_dump_json(indent=2)}")
        except ValueError:
            print("No payment response header found")

asyncio.run(main())
```

**동작 원리**: `x402HttpxClient`는 402 응답을 받으면 자동으로:
1. `PAYMENT-REQUIRED` 헤더에서 결제 요구사항 파싱
2. 등록된 메커니즘(EVM/SVM)으로 결제 페이로드 서명
3. `PAYMENT-SIGNATURE` 헤더에 서명 페이로드를 넣고 재요청
4. 200 응답을 받으면 `PAYMENT-RESPONSE` 헤더에서 정산 결과 추출

### 4.2 클라이언트 고급 설정

```python
from x402 import x402Client, x402ClientConfig, SchemeRegistration
from x402.mechanisms.evm.exact import ExactEvmScheme
from x402.mechanisms.svm.exact import ExactSvmScheme

# 설정 기반 초기화
config = x402ClientConfig(
    schemes=[
        SchemeRegistration(network="eip155:*", client=ExactEvmScheme(signer)),
        SchemeRegistration(network="solana:*", client=ExactSvmScheme(signer)),
    ],
    policies=[
        prefer_network("eip155:8453"),   # Base Mainnet 우선
        prefer_scheme("exact"),
        max_amount(1_000_000),           # 1 USDC 상한
    ],
)
client = x402Client.from_config(config)

# 라이프사이클 훅
client.on_before_payment_creation(lambda ctx: print(f"Paying on: {ctx.selected_requirements.network}"))
client.on_after_payment_creation(lambda ctx: print(f"Signed: {ctx.payment_payload}"))
client.on_payment_creation_failure(lambda ctx: print(f"Failed: {ctx.error}"))
```

---

## 5. Facilitator API

Facilitator는 결제 검증과 온체인 정산을 대행하는 서비스다.

### 5.1 사용 가능한 Facilitator

| Facilitator | URL | 인증 | 비용 |
|-------------|-----|------|------|
| x402.org (테스트넷) | `https://x402.org/facilitator` | 불필요 | 무료 |
| Coinbase CDP (프로덕션) | `https://api.cdp.coinbase.com/platform/v2/x402` | CDP API Key | 무료 1,000건/월, 이후 $0.001/건 |
| Cloudflare | x402 Foundation 멤버로 참여 | - | - |

### 5.2 Facilitator 엔드포인트

**POST /verify**
- 입력: `{ payload: PaymentPayload, requirements: PaymentRequirements }`
- 출력: `{ is_valid: boolean, ... }`
- 동기적, 빠름 (온체인 트랜잭션 없음)
- 서명 유효성, nonce, 만료 시간, 금액 등 검증

**POST /settle**
- 입력: `{ payload: PaymentPayload, requirements: PaymentRequirements }`
- 출력: `{ success: boolean, tx_hash: string, network: string, payer: string }`
- 비동기적, 블록체인 트랜잭션 발생
- 온체인 확인(confirmation) 대기 후 응답

**GET /supported**
- 지원 네트워크, 스킴, 토큰 목록 반환

### 5.3 네트워크 식별자 (CAIP-2 형식)

| 네트워크 | CAIP-2 ID |
|----------|-----------|
| Base Mainnet | `eip155:8453` |
| Base Sepolia (테스트넷) | `eip155:84532` |
| Polygon Mainnet | `eip155:137` |
| Solana Mainnet | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` |
| Solana Devnet | `solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1` |

---

## 6. V2 프로토콜 주요 변경사항 (2025-12 릴리스)

### 6.1 헤더 변경
- `X-*` 접두사 제거 (비표준이었음)
- 결제 요구사항이 응답 Body -> `PAYMENT-REQUIRED` 헤더로 이동
- 응답 Body를 에러 상세 정보 용도로 활용 가능

### 6.2 새로운 기능
- **세션 지원**: 이전 결제로 구매한 리소스에 대해 반복 온체인 결제 생략
- **동적 payTo 라우팅**: 요청별로 다른 수신 주소 지정 (마켓플레이스, 멀티테넌트)
- **지갑 기반 ID**: `SIGN-IN-WITH-X` 헤더 (CAIP-122 기반, 준비 중)
- **멀티체인 기본**: Base, Solana, 새로운 L2 체인
- **레거시 레일 호환**: ACH, SEPA, 카드 네트워크

### 6.3 하위 호환성
- **V1과 완전 하위 호환**. SDK가 V1/V2 헤더 모두 처리
- 새 기능은 Extensions로 추가 (코어 명세 변경 없음)

---

## 7. A2A + x402 통합 (google-agentic-commerce/a2a-x402)

A2A 프로토콜과 x402를 결합하여 에이전트 간 결제를 가능하게 하는 확장.

**리포지토리**: https://github.com/google-agentic-commerce/a2a-x402
**스타**: 473 / **라이선스**: Apache 2.0

### 통합 결제 플로우
1. 서비스 에이전트가 결제 조건 응답 (Payment Required)
2. 클라이언트 에이전트가 암호학적 서명으로 결제 제출 (Payment Submitted)
3. 서비스 에이전트가 온체인 검증 후 서비스 제공 (Payment Completed)

### 프로젝트 구조
```
a2a-x402/
  spec/v0.1/spec.md         # 기술 명세
  schemes/                   # 실험적 결제 스킴
  python/
    x402_a2a/               # 코어 라이브러리
    examples/               # 실행 가능한 데모
```

설계 철학: "functional core, imperative shell" -- 코어는 순수 함수, 외부 통합은 Executor/미들웨어.

---

## 8. 빠른 시작 가이드

### 8.1 최소 서버 (FastAPI, EVM만)

```bash
pip install "x402[fastapi,evm]"
```

```python
# server.py
import os
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
        accepts=[
            PaymentOption(
                scheme="exact",
                pay_to=os.getenv("WALLET_ADDRESS"),
                price="$0.001",
                network="eip155:84532",
            ),
        ],
        description="Paid API endpoint",
    ),
}
app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=server)

@app.get("/api/data")
async def get_data():
    return {"result": "paid content"}
```

```bash
# .env
WALLET_ADDRESS=0xYourBaseSepoliaAddress

# 실행
uvicorn server:app --host 0.0.0.0 --port 4021
```

### 8.2 최소 클라이언트 (httpx)

```bash
pip install "x402[httpx,evm]"
```

```python
# client.py
import asyncio
from eth_account import Account
from x402 import x402Client
from x402.http.clients import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client

async def main():
    client = x402Client()
    account = Account.from_key("0xYOUR_PRIVATE_KEY")
    register_exact_evm_client(client, EthAccountSigner(account))

    async with x402HttpxClient(client) as http:
        response = await http.get("http://localhost:4021/api/data")
        await response.aread()
        print(response.json())

asyncio.run(main())
```

### 8.3 테스트넷 자금

- Base Sepolia ETH: https://faucet.cdp.coinbase.com
- Base Sepolia USDC: 같은 faucet에서 획득 가능
- Solana Devnet SOL: `solana airdrop 2`

---

## 9. 프로덕션 전환 체크리스트

| 항목 | 테스트넷 | 프로덕션 |
|------|---------|---------|
| Facilitator URL | `https://x402.org/facilitator` | `https://api.cdp.coinbase.com/platform/v2/x402` |
| 인증 | 불필요 | `CDP_API_KEY_ID` + `CDP_API_KEY_SECRET` |
| EVM 네트워크 | `eip155:84532` (Base Sepolia) | `eip155:8453` (Base Mainnet) |
| Solana 네트워크 | `solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1` | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` |
| USDC 컨트랙트 | 테스트넷 주소 | 메인넷 주소 |
| 비용 | 무료 | 1,000건/월 무료, 이후 $0.001/건 |

---

## 참고 자료

### 공식 리소스
- [coinbase/x402 GitHub](https://github.com/coinbase/x402) -- 메인 리포지토리 (모든 SDK 소스)
- [x402 PyPI 패키지](https://pypi.org/project/x402/) -- Python SDK (v2.3.0)
- [@coinbase/x402 npm](https://www.npmjs.com/package/@coinbase/x402) -- Coinbase Facilitator 패키지
- [@x402/express npm](https://www.npmjs.com/package/@x402/express) -- Express 미들웨어
- [@x402/paywall npm](https://www.npmjs.com/package/@x402/paywall) -- Paywall UI 컴포넌트
- [Coinbase x402 문서](https://docs.cdp.coinbase.com/x402/welcome) -- 공식 개발자 문서
- [x402 Seller Quickstart](https://docs.cdp.coinbase.com/x402/quickstart-for-sellers) -- 서버 구축 가이드
- [x402 Buyer Quickstart](https://docs.cdp.coinbase.com/x402/quickstart-for-buyers) -- 클라이언트 구축 가이드

### 공식 예제 코드
- [Python FastAPI 서버](https://github.com/coinbase/x402/tree/main/examples/python/servers/fastapi)
- [Python Flask 서버](https://github.com/coinbase/x402/tree/main/examples/python/servers/flask)
- [Python httpx 클라이언트](https://github.com/coinbase/x402/tree/main/examples/python/clients/httpx)
- [Python requests 클라이언트](https://github.com/coinbase/x402/tree/main/examples/python/clients/requests)
- [TypeScript Express 서버](https://github.com/coinbase/x402/tree/main/examples/typescript/servers/express)

### 프로토콜 명세 및 블로그
- [x402.org 공식 사이트](https://www.x402.org/)
- [x402 V2 Launch 블로그](https://www.x402.org/writing/x402-v2-launch)
- [x402 프로토콜 PDF 명세](https://www.x402.org/x402.pdf)
- [Coinbase x402 소개](https://www.coinbase.com/developer-platform/products/x402)
- [Facilitator API 레퍼런스](https://docs.cdp.coinbase.com/api-reference/v2/rest-api/x402-facilitator/x402-facilitator)

### 커뮤니티 구현
- [a2a-x402 (A2A + x402 통합)](https://github.com/google-agentic-commerce/a2a-x402)
- [x402-rs (Rust 구현)](https://github.com/x402-rs/x402-rs)
- [x402-dotnet (.NET 구현)](https://github.com/michielpost/x402-dotnet)
- [mcp-go-x402 (MCP Go 구현)](https://github.com/mark3labs/mcp-go-x402)
- [awesome-x402 (리소스 모음)](https://github.com/xpaysh/awesome-x402)

### 튜토리얼
- [QuickNode: x402 Paywall 구현 가이드](https://www.quicknode.com/guides/infrastructure/how-to-use-x402-payment-required)
- [Cloudflare x402 Foundation 발표](https://blog.cloudflare.com/x402/)
- [Circle x402 + USDC 가이드](https://www.circle.com/blog/autonomous-payments-using-circle-wallets-usdc-and-x402)
