# x402 V2 프로토콜 표준 스펙 검증 보고서

> 검증일: 2026-03-17
> 검증 소스: `github.com/coinbase/x402/specs/x402-specification-v2.md`, `specs/transports-v2/http.md`, `specs/x402-specification-v1.md`, `specs/transports-v1/http.md`

---

## 1. HTTP 헤더 이름 검증

### 공식 V2 스펙 (specs/transports-v2/http.md)

| 방향 | 헤더 이름 | 인코딩 | 판정 |
|------|-----------|--------|------|
| Server -> Client (402 응답) | `PAYMENT-REQUIRED` | Base64 JSON | **정확** |
| Client -> Server (결제 제출) | `PAYMENT-SIGNATURE` | Base64 JSON | **정확** |
| Server -> Client (정산 결과) | `PAYMENT-RESPONSE` | Base64 JSON | **정확** |

### V1 과의 차이 (specs/transports-v1/http.md)

| 목적 | V1 | V2 |
|------|----|----|
| 결제 요구사항 | **응답 Body** (JSON) | `PAYMENT-REQUIRED` **헤더** |
| 결제 서명 | `X-PAYMENT` | `PAYMENT-SIGNATURE` |
| 정산 결과 | `X-PAYMENT-RESPONSE` | `PAYMENT-RESPONSE` |

**결론: 우리 구현의 헤더 이름 3개 모두 V2 스펙과 일치한다.**

---

## 2. PAYMENT-REQUIRED 헤더 JSON 구조 검증

### 공식 V2 스펙 (PaymentRequired)

```json
{
  "x402Version": 2,
  "error": "string (optional)",
  "resource": {
    "url": "string (required)",
    "description": "string (optional)",
    "mimeType": "string (optional)"
  },
  "accepts": [
    {
      "scheme": "string",
      "network": "string (CAIP-2)",
      "amount": "string",
      "asset": "string",
      "payTo": "string",
      "maxTimeoutSeconds": "number",
      "extra": "object (optional)"
    }
  ],
  "extensions": "object (optional)"
}
```

### 우리 구현 (api/x402.py)

```json
{
  "x402Version": 2,
  "accepts": [
    {
      "scheme": "exact",
      "payTo": "0x...",
      "maxAmountRequired": "100000",
      "asset": "0x...",
      "network": "eip155:84532",
      "extra": {"name": "USDC", "version": "2"}
    }
  ]
}
```

### 필드별 검증 결과

| 필드 | V2 스펙 | 우리 구현 | 판정 |
|------|---------|-----------|------|
| `x402Version` | `2` | `2` | **정확** |
| `error` | optional string | 미포함 (Body에 넣음) | **허용됨** (optional) |
| `resource` | `{ url, description, mimeType }` 객체 | **미포함** | **누락** |
| `accepts[].scheme` | "exact" | "exact" | **정확** |
| `accepts[].network` | CAIP-2 형식 | "eip155:84532" | **정확** |
| `accepts[].amount` | V2 필드명 | **`maxAmountRequired` 사용** | **오류 -- V1 필드명** |
| `accepts[].asset` | 토큰 주소 | "0x036CbD..." | **정확** |
| `accepts[].payTo` | 지갑 주소 | "0x742d..." | **정확** |
| `accepts[].maxTimeoutSeconds` | number | 미포함 | **누락** (optional이므로 허용 가능) |
| `accepts[].extra` | optional object | `{"name": "USDC", "version": "2"}` | **정확** |
| `extensions` | optional object | 미포함 | **허용됨** (optional) |

### 핵심 오류

1. **`maxAmountRequired`는 V1 필드명이다. V2에서는 `amount`로 변경되었다.**
   - V1 스펙: `maxAmountRequired` (string)
   - V2 스펙: `amount` (string, atomic token units)

2. **`resource` 객체가 누락되었다.** V2에서는 PaymentRequirements 밖으로 분리되어 별도의 `resource` 객체로 존재한다.
   - V1: `resource`, `description`, `mimeType`이 accepts 배열 내부에 있었음
   - V2: `resource: { url, description, mimeType }` 가 PaymentRequired 최상위 레벨로 이동

---

## 3. PAYMENT-SIGNATURE 헤더 JSON 구조 검증

### 공식 V2 스펙 (PaymentPayload)

```json
{
  "x402Version": 2,
  "resource": {
    "url": "string (optional)",
    "description": "string (optional)",
    "mimeType": "string (optional)"
  },
  "accepted": {
    "scheme": "string",
    "network": "string",
    "amount": "string",
    "asset": "string",
    "payTo": "string",
    "maxTimeoutSeconds": "number",
    "extra": "object (optional)"
  },
  "payload": {
    "signature": "string (EIP-712 hex)",
    "authorization": {
      "from": "string",
      "to": "string",
      "value": "string",
      "validAfter": "string (Unix timestamp)",
      "validBefore": "string (Unix timestamp)",
      "nonce": "string (32-byte hex)"
    }
  },
  "extensions": "object (optional)"
}
```

### 우리 구현 (api/x402.py verify_payment_signature에서 기대하는 구조)

```python
# decoded["scheme"]      -- 최상위 scheme
# decoded["network"]     -- 최상위 network
# decoded["payload"]["authorization"]["from"]
# decoded["payload"]["authorization"]["to"]
# decoded["payload"]["authorization"]["value"]
# decoded["payload"]["authorization"]["validBefore"]
```

### 필드별 검증 결과

| 필드 | V2 스펙 | 우리 구현이 기대하는 것 | 판정 |
|------|---------|----------------------|------|
| `x402Version` | 최상위에 `2` | 확인 안 함 | 누락 |
| `resource` | `{ url, ... }` 객체 | 확인 안 함 | 허용 (검증 불필요) |
| `accepted` | 선택된 PaymentRequirements 전체 객체 | 없음 | **누락** |
| `scheme` | `accepted.scheme` (중첩) | `decoded["scheme"]` (최상위) | **오류 -- V1 구조** |
| `network` | `accepted.network` (중첩) | `decoded["network"]` (최상위) | **오류 -- V1 구조** |
| `payload.signature` | EIP-712 hex string | 확인 안 함 (시뮬레이션) | 허용 |
| `payload.authorization.from` | payer address | `auth["from"]` | **정확** |
| `payload.authorization.to` | recipient address | `auth["to"]` | **정확** |
| `payload.authorization.value` | atomic units string | `auth["value"]` | **정확** |
| `payload.authorization.validAfter` | Unix timestamp string | 확인 안 함 | 누락 |
| `payload.authorization.validBefore` | Unix timestamp string | `auth["validBefore"]` | **정확** |
| `payload.authorization.nonce` | 32-byte hex string | 확인 안 함 | 허용 (시뮬레이션) |

### 핵심 오류

1. **V2에서 `scheme`과 `network`는 최상위가 아니라 `accepted` 객체 안에 있다.**
   - V1: `{ x402Version, scheme, network, payload: {...} }` -- 최상위에 scheme, network
   - V2: `{ x402Version, accepted: { scheme, network, amount, ... }, payload: {...} }` -- accepted 안에 중첩

2. **`accepted` 필드가 누락되었다.** V2에서 클라이언트는 서버가 보낸 accepts 배열 중 선택한 것을 `accepted`에 그대로 넣어야 한다.

---

## 4. PAYMENT-RESPONSE 헤더 JSON 구조 검증

### 공식 V2 스펙 (SettlementResponse)

```json
{
  "success": true,
  "payer": "string (optional)",
  "transaction": "string (blockchain hash)",
  "network": "string (CAIP-2)",
  "errorReason": "string (optional, omitted if successful)",
  "extensions": "object (optional)"
}
```

### 우리 구현 (api/x402.py create_payment_response)

```json
{
  "success": true,
  "network": "eip155:84532",
  "tx_hash": "0x...",
  "payer": "0x..."
}
```

### 필드별 검증 결과

| 필드 | V2 스펙 | 우리 구현 | 판정 |
|------|---------|-----------|------|
| `success` | boolean | `true` | **정확** |
| `payer` | optional string | "0x..." | **정확** |
| `transaction` | blockchain hash string | **`tx_hash` 사용** | **오류 -- 필드명이 다름** |
| `network` | CAIP-2 string | "eip155:84532" | **정확** |
| `errorReason` | optional string (실패 시) | 미포함 | **허용됨** (성공 시 생략 가능) |
| `extensions` | optional object | 미포함 | **허용됨** (optional) |

### 핵심 오류

1. **트랜잭션 해시 필드명이 `tx_hash`가 아니라 `transaction`이다.**
   - V2 스펙: `"transaction": "0x..."`
   - 우리 구현: `"tx_hash": "0x..."` -- 잘못된 필드명

---

## 5. Facilitator 엔드포인트 검증

### POST /verify

**공식 요청 구조:**
```json
{
  "x402Version": 2,
  "paymentPayload": { /* PaymentPayload 전체 */ },
  "paymentRequirements": { /* PaymentRequirements 전체 */ }
}
```

**공식 성공 응답:**
```json
{
  "isValid": true,
  "payer": "0x..."
}
```

**공식 실패 응답:**
```json
{
  "isValid": false,
  "invalidReason": "insufficient_funds",
  "payer": "0x..."
}
```

### POST /settle

**공식 요청 구조:** /verify와 동일

**공식 성공 응답:**
```json
{
  "success": true,
  "payer": "0x...",
  "transaction": "0x...",
  "network": "eip155:84532"
}
```

**공식 실패 응답:**
```json
{
  "success": false,
  "errorReason": "insufficient_funds",
  "payer": "0x...",
  "transaction": "",
  "network": "eip155:84532"
}
```

### GET /supported

**공식 응답:**
```json
{
  "kinds": [
    {
      "x402Version": 2,
      "scheme": "exact",
      "network": "eip155:84532",
      "extra": {}
    }
  ],
  "extensions": ["string array"],
  "signers": {
    "eip155:*": ["0x..."],
    "solana:*": ["..."]
  }
}
```

### 우리 x402-research.md 문서의 기술 내용 검증

| 항목 | 문서 내용 | V2 스펙 | 판정 |
|------|----------|---------|------|
| /verify 요청 필드 | `payload`, `requirements` | `paymentPayload`, `paymentRequirements` | **필드명 부정확** |
| /verify 응답 | `is_valid` | `isValid` | **필드명 부정확** (snake_case vs camelCase) |
| /settle 응답 | `tx_hash` | `transaction` | **필드명 부정확** |
| /supported 응답 | 대략적으로 기술 | `kinds`, `extensions`, `signers` | 미기술 |

---

## 6. V1 vs V2 차이점 종합 정리

### 6.1 HTTP Transport 레이어

| 항목 | V1 | V2 |
|------|----|----|
| 결제 요구사항 전달 | **응답 Body** (JSON) | **PAYMENT-REQUIRED 헤더** (Base64 JSON) |
| 결제 서명 전달 | `X-PAYMENT` 헤더 | `PAYMENT-SIGNATURE` 헤더 |
| 정산 결과 전달 | `X-PAYMENT-RESPONSE` 헤더 | `PAYMENT-RESPONSE` 헤더 |
| X- 접두사 | 사용 | **제거** |

### 6.2 PaymentRequired 구조

| 항목 | V1 | V2 |
|------|----|----|
| 금액 필드 | `maxAmountRequired` | `amount` |
| 네트워크 형식 | `"base-sepolia"`, `"base"` | `"eip155:84532"`, `"eip155:8453"` (CAIP-2) |
| 리소스 위치 | accepts 배열 내부 (`resource`, `description`, `mimeType`) | 최상위 `resource` 객체로 분리 |
| Extensions | 없음 | `extensions` 객체 추가 |
| 응답 타입명 | `PaymentRequirementsResponse` | `PaymentRequired` |

### 6.3 PaymentPayload 구조

| 항목 | V1 | V2 |
|------|----|----|
| scheme 위치 | 최상위 (`payload.scheme`) | `accepted` 객체 내부 |
| network 위치 | 최상위 (`payload.network`) | `accepted` 객체 내부 |
| 선택 정보 | 없음 (scheme + network만) | `accepted` 객체 (선택한 PaymentRequirements 전체) |
| resource 참조 | 없음 | `resource` 객체 (optional) |
| Extensions | 없음 | `extensions` 객체 추가 |

### 6.4 SettlementResponse 구조

| 항목 | V1 | V2 |
|------|----|----|
| 구조 | 거의 동일 | `extensions` 추가 |
| tx 필드 | `transaction` | `transaction` (동일) |

### 6.5 Facilitator API

| 항목 | V1 | V2 |
|------|----|----|
| /supported 응답 | `kinds` 만 | `kinds` + `extensions` + `signers` |
| Discovery API | 없음 | `GET /discovery/resources` 추가 |

---

## 7. 오류 요약 및 수정 가이드

### 반드시 수정해야 할 오류 (스펙 불일치)

| # | 위치 | 현재값 | 올바른 값 | 심각도 |
|---|------|--------|-----------|--------|
| 1 | `api/x402.py` PaymentRequired | `maxAmountRequired` | `amount` | **높음** -- V1 필드명 |
| 2 | `api/x402.py` PaymentRequired | `resource` 객체 없음 | `resource: { url }` 추가 필요 | **중간** |
| 3 | `api/x402.py` verify 로직 | `decoded["scheme"]` (최상위) | `decoded["accepted"]["scheme"]` | **높음** -- V1 구조 |
| 4 | `api/x402.py` verify 로직 | `decoded["network"]` (최상위) | `decoded["accepted"]["network"]` | **높음** -- V1 구조 |
| 5 | `api/x402.py` SettlementResponse | `tx_hash` | `transaction` | **높음** -- 필드명 오류 |
| 6 | `code_flow.md` 전체 | V1 스펙 기준 (`X-PAYMENT` 등) | V2 스펙으로 업데이트 필요 | **중간** -- 문서 |

### 수정 예시: api/x402.py PaymentRequired

```python
# 수정 전 (V1 혼용)
payment_requirements = {
    "x402Version": 2,
    "accepts": [{
        "scheme": "exact",
        "payTo": PAY_TO,
        "maxAmountRequired": PRICE,  # <-- V1 필드명
        "asset": ASSET,
        "network": NETWORK,
        "extra": {"name": "USDC", "version": "2"},
    }],
}

# 수정 후 (V2 준수)
payment_requirements = {
    "x402Version": 2,
    "resource": {
        "url": "/chat",
        "description": "Soul Store chat interaction",
        "mimeType": "application/json",
    },
    "accepts": [{
        "scheme": "exact",
        "payTo": PAY_TO,
        "amount": PRICE,  # <-- V2 필드명
        "asset": ASSET,
        "network": NETWORK,
        "maxTimeoutSeconds": 3600,
        "extra": {"name": "USDC", "version": "2"},
    }],
}
```

### 수정 예시: api/x402.py verify (PaymentPayload 파싱)

```python
# 수정 전 (V1 구조)
if decoded.get("scheme") != "exact":
    return None
if decoded.get("network") != NETWORK:
    return None

# 수정 후 (V2 구조)
accepted = decoded.get("accepted", {})
if accepted.get("scheme") != "exact":
    return None
if accepted.get("network") != NETWORK:
    return None
```

### 수정 예시: api/x402.py SettlementResponse

```python
# 수정 전
response_data = {
    "success": True,
    "network": NETWORK,
    "tx_hash": "0x" + secrets.token_hex(32),  # <-- 잘못된 필드명
    "payer": payer,
}

# 수정 후
response_data = {
    "success": True,
    "network": NETWORK,
    "transaction": "0x" + secrets.token_hex(32),  # <-- V2 표준 필드명
    "payer": payer,
}
```

---

## 8. week-6 데모 (code_flow.md) 문서 현황

`study/week-6/demos/x402/code_flow.md`는 **완전히 V1 기준**으로 작성되어 있다:

- `X-PAYMENT` 헤더 사용 (V1)
- 플랫 PaymentPayload 구조 (`version`, `from`, `to`, `amount`, `chain` 등 -- 비표준)
- 네트워크를 `"base"` 로 표기 (V1 -- CAIP-2 아님)
- Facilitator API 미기술

이 문서는 **학습용 단순화 데모**로서의 가치는 있으나, V2 스펙과는 일치하지 않는다.

---

## 참고 자료

- [coinbase/x402 GitHub - V2 Spec](https://github.com/coinbase/x402/blob/main/specs/x402-specification-v2.md)
- [coinbase/x402 GitHub - V2 HTTP Transport](https://github.com/coinbase/x402/blob/main/specs/transports-v2/http.md)
- [coinbase/x402 GitHub - V1 Spec](https://github.com/coinbase/x402/blob/main/specs/x402-specification-v1.md)
- [coinbase/x402 GitHub - V1 HTTP Transport](https://github.com/coinbase/x402/blob/main/specs/transports-v1/http.md)
- [Coinbase x402 공식 문서](https://docs.cdp.coinbase.com/x402/)
- [x402.org 공식 사이트](https://www.x402.org/)
