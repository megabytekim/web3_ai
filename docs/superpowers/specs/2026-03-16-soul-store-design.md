# Agent M Soul Store — A2A + x402 Integration Design

> Date: 2026-03-16
> Status: Draft
> Project: study/implemenation/a2a-gemini-agent/

## Overview

Agent M (Matrix의 Morpheus 캐릭터 A2A 챗 에이전트)에 **영혼 저장소** 기능을 추가한다. 사용자가 대화를 간직하고 싶다는 의사를 표현하면, Agent M이 결제 페이지 링크를 제공하고, x402 프로토콜로 결제 후 랜덤 아이템(영혼석, 금고, 수정구 등)에 대화 요약이 담겨 나온다.

**목표**: A2A + x402 프로토콜 결합 데모 (해커톤/프로토타입 수준)
**핵심 제약**: 온체인 결제는 시뮬레이션하되, x402 V2 프로토콜 흐름과 헤더 포맷은 정확히 따름

---

## 1. 전체 흐름

```
사용자 ─── /chat ───> Agent M (A2A + Gemini)
                         │
            "이 대화를 간직하고 싶어"
            (Gemini가 맥락에서 자연스럽게 감지)
                         │
            Agent M: "자네의 깨달음을 영원히 담아둘 곳이 있다네...
                      [영혼 저장소로 가게](/soul-store?ctx=xxx)"
                         │
사용자 ─── /soul-store?ctx=xxx ───> 결제 페이지 (pay.html)
                         │
                    "결제하기" 클릭
                         │
    ┌─── 프로토콜 시각화 (위→아래, 1초 간격) ───┐
    │                                            │
    │  ① GET /api/soul-vault?ctx=xxx             │
    │  ② 402 + PAYMENT-REQUIRED 헤더             │
    │  ③ 시뮬레이션 서명 생성                      │
    │  ④ GET + PAYMENT-SIGNATURE 헤더            │
    │  ⑤ Facilitator 검증 (시뮬레이션)            │
    │  ⑥ 200 OK + PAYMENT-RESPONSE 헤더          │
    │                                            │
    └────────────────────────────────────────────┘
                         │
              아이템 공개 연출 + 대화 요약
```

---

## 2. x402 프로토콜 구현 (시뮬레이션)

x402 V2 표준을 정확히 따르되, 블록체인 서명/정산만 시뮬레이션한다.

### 2.1 Step-by-step 프로토콜 흐름

```
Browser                    Soul Vault Server           Facilitator (시뮬레이션)
  │                              │                           │
  │── GET /api/soul-vault ──────>│                           │
  │   (PAYMENT-SIGNATURE 없음)   │                           │
  │                              │                           │
  │<── 402 Payment Required ─────│                           │
  │    PAYMENT-REQUIRED: <base64>│                           │
  │                              │                           │
  │   [브라우저: 시뮬레이션 서명 생성]                          │
  │                              │                           │
  │── GET /api/soul-vault ──────>│                           │
  │   PAYMENT-SIGNATURE: <base64>│                           │
  │                              │── verify(payload) ───────>│
  │                              │<── { is_valid: true } ────│
  │                              │                           │
  │<── 200 OK ───────────────────│                           │
  │    PAYMENT-RESPONSE: <base64>│                           │
  │    Body: { item, summary }   │                           │
  │                              │── settle(payload) ───────>│
  │                              │<── { tx_hash: "0x..." } ──│
```

### 2.2 PAYMENT-REQUIRED 헤더 (서버 → 브라우저)

402 응답 시 `PAYMENT-REQUIRED` 헤더에 base64 인코딩된 JSON:

```json
{
  "x402Version": 2,
  "accepts": [
    {
      "scheme": "exact",
      "payTo": "0xSIMULATED_RECEIVER_ADDRESS",
      "maxAmountRequired": "100000",
      "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
      "network": "eip155:84532",
      "extra": {
        "name": "USDC",
        "version": "2"
      }
    }
  ]
}
```

필드 설명:
- `x402Version`: 프로토콜 버전 (2)
- `scheme`: 결제 스킴 ("exact" = 정확한 금액 지불)
- `payTo`: 수신 지갑 주소 (시뮬레이션)
- `maxAmountRequired`: "100000" = 0.10 USDC (6 decimals)
- `asset`: Base Sepolia USDC 컨트랙트 주소
- `network`: CAIP-2 형식 네트워크 ID (Base Sepolia = eip155:84532)

### 2.3 PAYMENT-SIGNATURE 헤더 (브라우저 → 서버)

브라우저가 생성하는 시뮬레이션 결제 서명 (base64 인코딩된 JSON):

```json
{
  "scheme": "exact",
  "network": "eip155:84532",
  "payload": {
    "signature": "0xSIMULATED_SIGNATURE_...",
    "authorization": {
      "from": "0xSIMULATED_PAYER_ADDRESS",
      "to": "0xSIMULATED_RECEIVER_ADDRESS",
      "value": "100000",
      "validAfter": 0,
      "validBefore": "<dynamic: now + 3600>",
      "nonce": "0xRANDOM_NONCE"
    }
  }
}
```

`validBefore`는 **동적 생성** — 브라우저에서 `Math.floor(Date.now() / 1000) + 3600` (1시간 후).
실제 x402에서는 EIP-712 typed data로 서명하지만, 시뮬레이션에서는 SHA256 해시로 대체.

### 2.4 PAYMENT-RESPONSE 헤더 (서버 → 브라우저)

200 응답 시 `PAYMENT-RESPONSE` 헤더에 base64 인코딩된 JSON:

```json
{
  "success": true,
  "network": "eip155:84532",
  "tx_hash": "0xSIMULATED_TX_HASH_...",
  "payer": "0xSIMULATED_PAYER_ADDRESS"
}
```

### 2.5 시뮬레이션 범위

| 구성 요소 | 실제 구현 | 시뮬레이션 |
|-----------|----------|-----------|
| HTTP 402 응답 | O | - |
| PAYMENT-REQUIRED 헤더 포맷 | O | - |
| PAYMENT-SIGNATURE 헤더 포맷 | O | - |
| PAYMENT-RESPONSE 헤더 포맷 | O | - |
| base64 인코딩 | O | - |
| EIP-712 서명 | - | SHA256 해시 |
| Facilitator verify 호출 | - | 로컬 검증 함수 |
| Facilitator settle 호출 | - | 가짜 tx_hash 생성 |
| 온체인 USDC 전송 | - | 생략 |
| 지갑 연결 (MetaMask) | - | 시뮬레이션 주소 |

---

## 3. Agent M 의도 감지

기존 `SYSTEM_INSTRUCTION`에 추가:

```
추가 능력 — 영혼 저장소:
- 상대방이 대화를 기억하고 싶다, 저장하고 싶다, 간직하고 싶다,
  영혼을 어딘가에 담고 싶다는 뉘앙스를 감지하면
  영혼 저장소 링크를 자연스럽게 제안하게.
- 반드시 대화의 흐름 속에서 자연스럽게. 예:
  "자네의 깨달음을 영원히 담아둘 곳이 있다네...
   [영혼 저장소로 가게](SOUL_STORE_LINK)"
- "SOUL_STORE_LINK" 라는 문자열을 그대로 출력하게. 시스템이 알아서 실제 URL로 바꿔줌.
- 항상 마크다운 링크로 제공
- 너무 이르게 제안하지 말 것 (최소 2-3턴 대화 후)
- 상대가 관심 없으면 강요하지 말 것
```

### 3.1 contextId 주입 메커니즘

Gemini는 A2A 프로토콜의 `contextId` 값에 직접 접근할 수 없다. 따라서:

1. 시스템 프롬프트에서 Gemini에게 `SOUL_STORE_LINK` 플레이스홀더를 출력하도록 지시
2. `GeminiChatExecutor.execute()`에서 Gemini 응답 텍스트를 후처리
3. 이렇게 하면 Gemini는 URL 구조를 몰라도 되고, 실제 contextId가 정확히 삽입됨

정확한 수정 위치 (`execute()` 메서드):
```python
async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
    user_text = context.get_user_input()
    ctx_id = context.context_id or "default"

    reply = await self._get_gemini_response(ctx_id, user_text)
    # 후처리: 플레이스홀더를 실제 URL로 치환
    reply = reply.replace("SOUL_STORE_LINK", f"/soul-store?ctx={ctx_id}")
    await event_queue.enqueue_event(new_agent_text_message(reply))
```

참고: `_get_gemini_response()`는 히스토리에 Gemini의 원본 응답(플레이스홀더 포함)을 저장한다. 이는 의도된 동작 — Gemini는 후속 턴에서 자신이 출력한 `SOUL_STORE_LINK`를 보지만, 사용자에게 전달되는 메시지에서는 실제 URL로 치환됨.

### 3.2 chat.html 마크다운 링크 렌더링

Agent M 응답에서 마크다운 링크 `[텍스트](url)`를 클릭 가능한 `<a>` 태그로 변환. XSS 방지를 위해 `escapeHtml()` 이후에 적용하고, URL은 `/`로 시작하는 상대 경로만 허용:

```javascript
// escapeHtml(text) 적용 후:
escaped = escaped.replace(
  /\[([^\]]+)\]\((\/[^)]+)\)/g,
  '<a href="$2" target="_blank" style="color:#00ff41">$1</a>'
);
```

- `\/`로 시작하는 URL만 매칭 → `javascript:` XSS 차단
- `escapeHtml()` 이후에 적용 → HTML 인젝션 불가

---

## 4. 아이템 시스템

### 4.1 아이템 목록

| 아이템 | Rarity | 확률 | 색상 | Emoji |
|--------|--------|------|------|-------|
| 영혼석 | Common | 50% | 흰색 (#ffffff) | 💎 |
| 금고 | Uncommon | 25% | 초록 (#00ff41) | 🗄️ |
| 수정구 | Rare | 15% | 파랑 (#4169e1) | 🔮 |
| 불사조의 깃털 | Epic | 8% | 보라 (#9b59b6) | 🪶 |
| 네오의 선글라스 | Legendary | 2% | 금색 (#ffd700) | 🕶️ |

### 4.2 대화 요약

결제 성공 후, 해당 `contextId`의 대화 히스토리를 Gemini에게 전달하여 Agent M 말투로 요약 생성.

프롬프트 예시:
```
아래 대화를 Agent M(모피어스) 말투로 3줄 이내로 요약해줘.
마치 영혼석/수정구에 새겨넣을 비문처럼.
```

### 4.3 저장

인메모리 (서버 재시작 시 소멸). 데모 수준이므로 DB 불필요.
향후 확장 시 SQLite 또는 Vercel KV로 전환 가능.

---

## 5. 결제 페이지 UX — 프로토콜 시각화

`/soul-store?ctx=xxx` 페이지에서 "결제하기" 클릭 시, x402 프로토콜 각 단계가 위에서 아래로 순차적으로 나타남 (각 스텝 ~1초 간격, fade-in + slide-down).

### 5.1 시각화 스텝

```
┌──────────────────────────────────────────────────────┐
│  🔮 영혼 저장소 — x402 Payment Protocol               │
│  Price: 0.10 USDC (Base Sepolia Testnet)              │
│                                                       │
│  ① REQUEST                              [fade-in, 1s] │
│  ┌───────────────────────────────────────┐            │
│  │ GET /api/soul-vault?ctx=abc123        │            │
│  │ Headers: (none)                       │            │
│  └───────────────────────────────────────┘            │
│                 │                                     │
│                 ▼                                     │
│  ② 402 PAYMENT REQUIRED                 [fade-in, 2s] │
│  ┌───────────────────────────────────────┐            │
│  │ Status: 402 Payment Required          │            │
│  │ PAYMENT-REQUIRED: eyJ4NDAy...         │            │
│  │ ┌─ decoded ────────────────────────┐  │            │
│  │ │ x402Version: 2                   │  │            │
│  │ │ scheme: "exact"                  │  │            │
│  │ │ payTo: 0x1234...abcd             │  │            │
│  │ │ maxAmountRequired: 100000        │  │            │
│  │ │ asset: USDC                      │  │            │
│  │ │ network: eip155:84532            │  │            │
│  │ └─────────────────────────────────┘  │            │
│  └───────────────────────────────────────┘            │
│                 │                                     │
│                 ▼                                     │
│  ③ SIGNING PAYMENT                      [fade-in, 3s] │
│  ┌───────────────────────────────────────┐            │
│  │ 🔐 Generating payment signature...    │            │
│  │ from: 0xaaaa...bbbb (simulated)       │            │
│  │ to:   0x1234...abcd                   │            │
│  │ value: 100000 (0.10 USDC)             │            │
│  │ nonce: 0x7f3a...                      │            │
│  │ signing...  ████████████░░ 85%        │            │
│  └───────────────────────────────────────┘            │
│                 │                                     │
│                 ▼                                     │
│  ④ RETRY WITH PAYMENT                   [fade-in, 4s] │
│  ┌───────────────────────────────────────┐            │
│  │ GET /api/soul-vault?ctx=abc123        │            │
│  │ PAYMENT-SIGNATURE: eyJzY2hl...        │            │
│  └───────────────────────────────────────┘            │
│                 │                                     │
│                 ▼                                     │
│  ⑤ FACILITATOR VERIFY                   [fade-in, 5s] │
│  ┌───────────────────────────────────────┐            │
│  │ POST x402.org/facilitator/verify      │            │
│  │ → { is_valid: true } ✅               │            │
│  └───────────────────────────────────────┘            │
│                 │                                     │
│                 ▼                                     │
│  ⑥ 200 OK + SETTLEMENT                  [fade-in, 6s] │
│  ┌───────────────────────────────────────┐            │
│  │ Status: 200 OK                        │            │
│  │ PAYMENT-RESPONSE: eyJzdWNj...         │            │
│  │ ┌─ decoded ────────────────────────┐  │            │
│  │ │ success: true                    │  │            │
│  │ │ tx_hash: 0x9f8e...              │  │            │
│  │ │ network: eip155:84532            │  │            │
│  │ └─────────────────────────────────┘  │            │
│  │ Body: { item: "수정구", rarity: ... } │            │
│  └───────────────────────────────────────┘            │
│                 │                                     │
│                 ▼                                     │
│  ✨ ITEM REVEAL                          [fade-in, 7s] │
│                                                       │
│            🔮 수정구 (Rare)                            │
│     ┌─────────────────────────────┐                   │
│     │  "자네는 오늘 AI의 본질에    │                   │
│     │   대해 깊은 질문을 던졌네.   │                   │
│     │   그 깨달음은 이 수정구에    │                   │
│     │   영원히 남으리라..."        │                   │
│     └─────────────────────────────┘                   │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### 5.2 실제 네트워크 동작

시각화는 7스텝이지만, 실제 HTTP 요청은 2번:

1. **①에서**: `GET /api/soul-vault?ctx=xxx` → 서버가 402 반환 (②의 데이터)
2. **④에서**: `GET /api/soul-vault?ctx=xxx` + `PAYMENT-SIGNATURE` 헤더 → 서버가 검증(⑤) 후 200 반환 (⑥의 데이터)

③ 서명 생성과 ⑤ Facilitator 검증은 시뮬레이션 (로컬 처리).

### 5.3 스타일

- Matrix 테마 (검정 배경 #0a0a0a, 초록 텍스트 #00ff41, 모노스페이스)
- chat.html과 동일한 스타일 베이스
- 각 스텝 박스: 반투명 border, 나타날 때 fade-in + slide-down
- 아이템 공개: rarity별 글로우 색상 + 스케일 애니메이션

---

## 6. 파일 구조

```
api/
  index.py          ← 기존 A2A 에이전트 (라우트 추가 + 시스템 프롬프트 수정)
  state.py          ← [신규] 공유 상태 (gemini_client, chat_histories)
  x402.py           ← [신규] 402 응답 생성 + PAYMENT-SIGNATURE 검증
  soul_store.py     ← [신규] 아이템 뽑기 + Gemini 대화 요약
  pay.html          ← [신규] 결제 UI + 프로토콜 시각화
  chat.html         ← 기존 (마크다운 링크 렌더링 추가)
tests/
  test_executor.py  ← 기존
  test_x402.py      ← [신규] x402 프로토콜 테스트
  test_soul_store.py← [신규] 아이템/요약 테스트
  conftest.py       ← 기존 (state.py mock 추가)
```

### 6.1 모듈 책임

**`api/x402.py`**
- `create_payment_required_response()` → Starlette `Response` 객체 (status=402, PAYMENT-REQUIRED 헤더)
- `verify_payment_signature(header_value: str) -> str | None` — base64 디코딩 후 JSON 구조 검증. 유효하면 payer 주소 반환, 아니면 None:
  - `scheme`, `network`, `payload` 필드 존재 확인
  - `payload.authorization.to`가 수신 주소와 일치하는지 확인
  - `payload.authorization.value`가 요구 금액 이상인지 확인
  - `payload.authorization.validBefore` > 현재 시간 확인
  - 서명 자체는 검증하지 않음 (시뮬레이션) — 구조만 올바르면 `payload.authorization.from` 반환
- `create_payment_response(payer: str) -> str` → PAYMENT-RESPONSE 헤더 값 (base64 JSON)
- 프로토콜 상수: `NETWORK = "eip155:84532"`, `ASSET`, `PAY_TO`, `PRICE`

**`api/soul_store.py`**
- `draw_item() -> dict` → 가중치 기반 랜덤 아이템 뽑기. 반환: `{"name", "rarity", "emoji", "color"}`
- `summarize_conversation(client, history) -> str` → Gemini로 대화 요약 생성
- `ITEMS` 목록 + rarity 정의

**`api/index.py` 수정**
- 라우트 추가: `/soul-store` (HTML), `/api/soul-vault` (x402 엔드포인트)
- `SYSTEM_INSTRUCTION`에 영혼 저장소 지시 추가
- `_chat_histories`를 모듈 레벨 dict로 리팩토링 (아래 6.3 참조)

### 6.3 공유 상태: `api/state.py`

순환 임포트를 방지하기 위해, `index.py`와 `soul_store.py`가 공유하는 상태를 별도 모듈로 분리:

```python
# api/state.py (신규 파일)
"""Shared state between A2A executor and Soul Store."""
from google import genai
from google.genai import types as genai_types

# 모듈 레벨 싱글톤
gemini_client: genai.Client = genai.Client()
chat_histories: dict[str, list[genai_types.Content]] = {}
```

각 모듈에서 임포트:
```python
# api/index.py
from api.state import gemini_client, chat_histories

class GeminiChatExecutor(AgentExecutor):
    def __init__(self) -> None:
        self._client = gemini_client
        self._chat_histories = chat_histories

# api/soul_store.py
from api.state import gemini_client, chat_histories
```

이렇게 하면:
- `index.py ↔ soul_store.py` 순환 임포트 없음
- Gemini 클라이언트도 싱글톤으로 공유
- `state.py`는 외부 임포트 없이 독립적

### 6.4 `/api/soul-vault` 라우트 핸들러

```python
async def _soul_vault_api(request):
    """x402 payment endpoint for Soul Store."""
    from starlette.responses import JSONResponse
    from api.state import gemini_client, chat_histories
    from api.x402 import (
        create_payment_required_response,
        verify_payment_signature,
        create_payment_response,
    )
    from api.soul_store import draw_item, summarize_conversation

    # 1. ctx 파라미터 확인
    ctx = request.query_params.get("ctx")
    if not ctx:
        return JSONResponse({"error": "ctx parameter required"}, status_code=400)

    # 2. 대화 히스토리 존재 확인
    if ctx not in chat_histories:
        return JSONResponse({"error": "conversation not found"}, status_code=404)

    # 3. PAYMENT-SIGNATURE 헤더 확인
    payment_sig = request.headers.get("payment-signature")

    if not payment_sig:
        # x402 Step 1: 402 Payment Required 반환
        return create_payment_required_response()

    # 4. 결제 검증 (시뮬레이션)
    payer = verify_payment_signature(payment_sig)
    if not payer:
        return JSONResponse({"error": "invalid payment signature"}, status_code=400)

    # 5. 아이템 뽑기
    item = draw_item()

    # 6. 대화 요약 (히스토리 스냅샷으로 race condition 방지)
    history_snapshot = list(chat_histories[ctx])
    summary = await summarize_conversation(gemini_client, history_snapshot)

    # 7. 200 + PAYMENT-RESPONSE 헤더 + JSON body
    body = {
        "item": item,
        "summary": summary,
        "payment": {
            "tx_hash": create_payment_response(payer)["tx_hash"],
            "network": "eip155:84532",
            "amount": "100000",
            "asset": "USDC",
        },
    }
    payment_response_header = create_payment_response(payer)
    return JSONResponse(
        body,
        headers={"PAYMENT-RESPONSE": base64_encode(payment_response_header)},
    )
```

`verify_payment_signature` 반환값 변경: `bool` → `str | None` (payer 주소 또는 None). 이래야 PAYMENT-RESPONSE에 payer를 포함 가능.

### 6.5 Starlette 라우팅 순서

`Mount("/", app=_a2a_app)` 은 catch-all이므로, 새 라우트를 **반드시 Mount 앞에** 배치:

```python
app = Starlette(routes=[
    Route("/chat", _chat_ui),
    Route("/soul-store", _soul_store_ui),                          # Mount 앞
    Route("/api/soul-vault", _soul_vault_api, methods=["GET", "OPTIONS"]),  # Mount 앞
    Mount("/", app=_a2a_app),                                      # catch-all은 마지막
])
```

### 6.6 pay.html 서빙 방식

`pay.html`은 정적 HTML로 로드하고, `ctx` 값은 JavaScript에서 `window.location.search`로 파싱:

```javascript
const params = new URLSearchParams(window.location.search);
const ctx = params.get('ctx');
// 이후 fetch('/api/soul-vault?ctx=' + ctx) 호출
```

서버사이드 템플릿 처리 불필요 — `chat.html`과 동일한 패턴.

### 6.7 에러 처리

| 상황 | 응답 |
|------|------|
| `ctx` 파라미터 없음 | 400 `{"error": "ctx parameter required"}` |
| `ctx`에 해당하는 대화 히스토리 없음 | 404 `{"error": "conversation not found"}` |
| `PAYMENT-SIGNATURE` 헤더 base64 디코딩 실패 | 400 `{"error": "invalid payment signature encoding"}` |
| `PAYMENT-SIGNATURE` JSON 구조 불일치 | 400 `{"error": "invalid payment signature format"}` |
| Gemini 요약 생성 실패 | 200 반환하되 summary를 기본값으로: `"(영혼의 기록을 해독할 수 없었네...)"` |

### 6.8 200 응답 본문 스키마

```json
{
  "item": {
    "name": "수정구",
    "rarity": "rare",
    "emoji": "🔮",
    "color": "#4169e1"
  },
  "summary": "자네는 오늘 AI의 본질에 대해 깊은 질문을 던졌네...",
  "payment": {
    "tx_hash": "0xSIMULATED...",
    "network": "eip155:84532",
    "amount": "100000",
    "asset": "USDC"
  }
}
```

### 6.9 CORS / Preflight 처리

`pay.html`에서 `/api/soul-vault`로 보내는 `GET` 요청에 커스텀 헤더 `PAYMENT-SIGNATURE`가 포함되면, 브라우저가 `OPTIONS` preflight 요청을 보낼 수 있다. 같은 origin이므로 CORS는 문제없지만, 커스텀 헤더는 "simple request" 범위를 벗어남.

해결: `_soul_vault_api` 핸들러에서 `OPTIONS` 메서드도 처리:
```python
if request.method == "OPTIONS":
    return Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Headers": "PAYMENT-SIGNATURE",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
        },
    )
```

라우트 정의 시 methods를 명시:
```python
Route("/api/soul-vault", _soul_vault_api, methods=["GET", "OPTIONS"]),
```

### 6.10 변경 요약

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `api/index.py` | 수정 | 라우트 추가, 시스템 프롬프트 수정, state.py 사용 |
| `api/state.py` | 신규 | 공유 상태 (gemini_client, chat_histories) |
| `api/x402.py` | 신규 | x402 V2 프로토콜 시뮬레이션 |
| `api/soul_store.py` | 신규 | 아이템 뽑기 + 대화 요약 |
| `api/pay.html` | 신규 | 결제 UI + 프로토콜 시각화 |
| `api/chat.html` | 수정 | 마크다운 링크 → `<a>` 태그 렌더링 |
| `tests/test_x402.py` | 신규 | x402 프로토콜 테스트 |
| `tests/test_soul_store.py` | 신규 | 아이템/요약 테스트 |
| `tests/conftest.py` | 수정 | state.py의 genai.Client mock 추가 |
| `pyproject.toml` | 변경 없음 | 추가 의존성 없음 |

---

## 7. 향후 확장 가능성 (현재 구현 범위 아님)

- **아이템별 차등 기능**: 영혼석은 전체 저장, 금고는 핵심만, 수정구는 명언 생성
- **NFT 민팅**: 아이템을 온체인 NFT로 발행
- **실제 x402 SDK 연동**: `pip install "x402[fastapi,evm]"` + Base Sepolia 테스트넷
- **영구 저장**: Vercel KV 또는 SQLite
- **@x402/paywall 프론트엔드**: 실제 지갑 연결 (MetaMask)
