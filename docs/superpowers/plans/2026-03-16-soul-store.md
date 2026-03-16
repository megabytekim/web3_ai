# Agent M Soul Store Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add x402-powered "Soul Store" to Agent M — users pay (simulated) to store conversation summaries in random magical items.

**Architecture:** Modular additions to the existing A2A Gemini agent. Shared state extracted to `api/state.py`. New `api/x402.py` handles x402 V2 protocol simulation. New `api/soul_store.py` handles item gacha + Gemini summarization. New `api/pay.html` provides Matrix-themed payment UI with step-by-step protocol visualization.

**Tech Stack:** Python 3.12, Starlette (ASGI), google-genai, a2a-sdk. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-03-16-soul-store-design.md`

---

## Chunk 1: Foundation — Shared State + Refactor

### Task 1: Create `api/state.py` and update test fixtures

**Files:**
- Create: `study/implemenation/a2a-gemini-agent/api/state.py`
- Modify: `study/implemenation/a2a-gemini-agent/tests/conftest.py`

- [ ] **Step 1: Create `api/state.py`**

```python
# study/implemenation/a2a-gemini-agent/api/state.py
"""Shared state between A2A executor and Soul Store."""

from google import genai
from google.genai import types as genai_types

# Module-level singletons
gemini_client: genai.Client = genai.Client()
chat_histories: dict[str, list[genai_types.Content]] = {}
```

- [ ] **Step 2: Update `conftest.py` to mock `state.py`**

Replace the existing `_mock_genai_client` fixture to patch `state.py`'s module-level client:

```python
# study/implemenation/a2a-gemini-agent/tests/conftest.py
"""Shared test fixtures for a2a-gemini-agent tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure the project root is on sys.path so `from api.index import ...` works.
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture(autouse=True)
def _mock_genai_client():
    """Patch genai.Client globally so tests never need a real API key."""
    mock_client = MagicMock()
    with patch("google.genai.Client", return_value=mock_client):
        yield


@pytest.fixture(autouse=True)
def _clear_chat_histories():
    """Clear shared chat_histories between tests."""
    from api.state import chat_histories
    chat_histories.clear()
    yield
    chat_histories.clear()
```

- [ ] **Step 3: Run existing tests to verify nothing breaks**

Run: `cd study/implemenation/a2a-gemini-agent && uv run pytest tests/ -v`
Expected: All 3 existing tests PASS (state.py exists but isn't used by index.py yet)

- [ ] **Step 4: Commit**

```bash
git add study/implemenation/a2a-gemini-agent/api/state.py study/implemenation/a2a-gemini-agent/tests/conftest.py
git commit -m "feat: add api/state.py for shared state, update test fixtures"
```

---

### Task 2: Refactor `api/index.py` to use `api/state.py`

**Files:**
- Modify: `study/implemenation/a2a-gemini-agent/api/index.py:10-11,53-55`

- [ ] **Step 1: Replace `genai.Client()` and `_chat_histories` with imports from `state.py`**

In `api/index.py`, make these changes:

Remove lines 10-11:
```python
from google import genai
from google.genai import types as genai_types
```

Replace with:
```python
from google.genai import types as genai_types

from api.state import gemini_client, chat_histories
```

Change `GeminiChatExecutor.__init__` (lines 53-55) from:
```python
    def __init__(self) -> None:
        self._client = genai.Client()
        self._chat_histories: dict[str, list[genai_types.Content]] = {}
```

To:
```python
    def __init__(self) -> None:
        self._client = gemini_client
        self._chat_histories = chat_histories
```

- [ ] **Step 2: Run existing tests to verify no regression**

Run: `cd study/implemenation/a2a-gemini-agent && uv run pytest tests/ -v`
Expected: All 3 tests PASS

- [ ] **Step 3: Commit**

```bash
git add study/implemenation/a2a-gemini-agent/api/index.py
git commit -m "refactor: use shared state from api/state.py in executor"
```

---

## Chunk 2: Backend Logic — x402 Protocol + Soul Store

### Task 3: Implement `api/x402.py` (TDD)

**Files:**
- Create: `study/implemenation/a2a-gemini-agent/tests/test_x402.py`
- Create: `study/implemenation/a2a-gemini-agent/api/x402.py`

- [ ] **Step 1: Write failing tests for x402 module**

```python
# study/implemenation/a2a-gemini-agent/tests/test_x402.py
"""Tests for x402 protocol simulation."""

import base64
import json
import time

import pytest


def test_create_payment_required_response_returns_402():
    """Should return a Starlette Response with status 402 and PAYMENT-REQUIRED header."""
    from api.x402 import create_payment_required_response

    response = create_payment_required_response()
    assert response.status_code == 402
    assert "payment-required" in response.headers


def test_payment_required_header_is_valid_base64_json():
    """PAYMENT-REQUIRED header should be base64-encoded JSON with x402 V2 structure."""
    from api.x402 import create_payment_required_response

    response = create_payment_required_response()
    header_value = response.headers["payment-required"]
    decoded = json.loads(base64.b64decode(header_value))

    assert decoded["x402Version"] == 2
    assert len(decoded["accepts"]) == 1
    accept = decoded["accepts"][0]
    assert accept["scheme"] == "exact"
    assert accept["network"] == "eip155:84532"
    assert "payTo" in accept
    assert "maxAmountRequired" in accept
    assert "asset" in accept


def test_verify_valid_payment_signature():
    """A structurally valid payment signature should return the payer address."""
    from api.x402 import PAY_TO, PRICE, verify_payment_signature

    payload = {
        "scheme": "exact",
        "network": "eip155:84532",
        "payload": {
            "signature": "0xFAKESIG",
            "authorization": {
                "from": "0xPAYER_ADDRESS",
                "to": PAY_TO,
                "value": PRICE,
                "validAfter": 0,
                "validBefore": int(time.time()) + 3600,
                "nonce": "0x1234",
            },
        },
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    result = verify_payment_signature(encoded)
    assert result == "0xPAYER_ADDRESS"


def test_verify_rejects_wrong_recipient():
    """Payment to wrong address should be rejected."""
    from api.x402 import PRICE, verify_payment_signature

    payload = {
        "scheme": "exact",
        "network": "eip155:84532",
        "payload": {
            "signature": "0xFAKESIG",
            "authorization": {
                "from": "0xPAYER",
                "to": "0xWRONG_ADDRESS",
                "value": PRICE,
                "validAfter": 0,
                "validBefore": int(time.time()) + 3600,
                "nonce": "0x1234",
            },
        },
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    result = verify_payment_signature(encoded)
    assert result is None


def test_verify_rejects_insufficient_amount():
    """Payment with insufficient amount should be rejected."""
    from api.x402 import PAY_TO, verify_payment_signature

    payload = {
        "scheme": "exact",
        "network": "eip155:84532",
        "payload": {
            "signature": "0xFAKESIG",
            "authorization": {
                "from": "0xPAYER",
                "to": PAY_TO,
                "value": "1",
                "validAfter": 0,
                "validBefore": int(time.time()) + 3600,
                "nonce": "0x1234",
            },
        },
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    result = verify_payment_signature(encoded)
    assert result is None


def test_verify_rejects_expired_payment():
    """Payment with validBefore in the past should be rejected."""
    from api.x402 import PAY_TO, PRICE, verify_payment_signature

    payload = {
        "scheme": "exact",
        "network": "eip155:84532",
        "payload": {
            "signature": "0xFAKESIG",
            "authorization": {
                "from": "0xPAYER",
                "to": PAY_TO,
                "value": PRICE,
                "validAfter": 0,
                "validBefore": int(time.time()) - 100,
                "nonce": "0x1234",
            },
        },
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    result = verify_payment_signature(encoded)
    assert result is None


def test_verify_rejects_malformed_base64():
    """Garbage input should return None, not crash."""
    from api.x402 import verify_payment_signature

    assert verify_payment_signature("not-valid-base64!!!") is None


def test_verify_rejects_missing_fields():
    """JSON missing required fields should return None."""
    from api.x402 import verify_payment_signature

    payload = {"scheme": "exact"}
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    assert verify_payment_signature(encoded) is None


def test_create_payment_response_returns_base64_json():
    """Should return base64-encoded JSON with tx_hash, network, payer."""
    from api.x402 import create_payment_response

    result = create_payment_response("0xPAYER")
    decoded = json.loads(base64.b64decode(result))
    assert decoded["success"] is True
    assert decoded["network"] == "eip155:84532"
    assert decoded["payer"] == "0xPAYER"
    assert decoded["tx_hash"].startswith("0x")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd study/implemenation/a2a-gemini-agent && uv run pytest tests/test_x402.py -v`
Expected: FAIL (ImportError — api.x402 doesn't exist yet)

- [ ] **Step 3: Implement `api/x402.py`**

```python
# study/implemenation/a2a-gemini-agent/api/x402.py
"""x402 V2 protocol simulation for Soul Store."""

import base64
import json
import secrets
import time

from starlette.responses import Response

# x402 V2 Protocol Constants
NETWORK = "eip155:84532"  # Base Sepolia
ASSET = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"  # USDC on Base Sepolia
PAY_TO = "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18"  # Simulated receiver
PRICE = "100000"  # 0.10 USDC (6 decimals)


def create_payment_required_response() -> Response:
    """Return a 402 response with PAYMENT-REQUIRED header (x402 V2 format)."""
    payment_requirements = {
        "x402Version": 2,
        "accepts": [
            {
                "scheme": "exact",
                "payTo": PAY_TO,
                "maxAmountRequired": PRICE,
                "asset": ASSET,
                "network": NETWORK,
                "extra": {"name": "USDC", "version": "2"},
            }
        ],
    }
    encoded = base64.b64encode(json.dumps(payment_requirements).encode()).decode()
    return Response(
        content=json.dumps({"error": "Payment Required", "x402Version": 2}),
        status_code=402,
        media_type="application/json",
        headers={"PAYMENT-REQUIRED": encoded},
    )


def verify_payment_signature(header_value: str) -> str | None:
    """Verify a PAYMENT-SIGNATURE header (simulated).

    Returns the payer address if valid, None otherwise.
    Checks structure and field values, but does NOT verify cryptographic signature.
    """
    try:
        decoded = json.loads(base64.b64decode(header_value))
    except Exception:
        return None

    try:
        payload = decoded["payload"]
        auth = payload["authorization"]

        # Check required fields exist
        if decoded.get("scheme") != "exact":
            return None
        if decoded.get("network") != NETWORK:
            return None

        # Check recipient
        if auth["to"] != PAY_TO:
            return None

        # Check amount
        if int(auth["value"]) < int(PRICE):
            return None

        # Check expiry
        if auth["validBefore"] <= time.time():
            return None

        return auth["from"]
    except (KeyError, TypeError, ValueError):
        return None


def create_payment_response(payer: str) -> str:
    """Create a base64-encoded PAYMENT-RESPONSE header value."""
    response_data = {
        "success": True,
        "network": NETWORK,
        "tx_hash": "0x" + secrets.token_hex(32),
        "payer": payer,
    }
    return base64.b64encode(json.dumps(response_data).encode()).decode()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd study/implemenation/a2a-gemini-agent && uv run pytest tests/test_x402.py -v`
Expected: All 9 tests PASS

- [ ] **Step 5: Run ALL tests to verify no regression**

Run: `cd study/implemenation/a2a-gemini-agent && uv run pytest tests/ -v`
Expected: All tests PASS (existing + new)

- [ ] **Step 6: Commit**

```bash
git add study/implemenation/a2a-gemini-agent/api/x402.py study/implemenation/a2a-gemini-agent/tests/test_x402.py
git commit -m "feat: add x402 V2 protocol simulation module"
```

---

### Task 4: Implement `api/soul_store.py` (TDD)

**Files:**
- Create: `study/implemenation/a2a-gemini-agent/tests/test_soul_store.py`
- Create: `study/implemenation/a2a-gemini-agent/api/soul_store.py`

- [ ] **Step 1: Write failing tests for soul_store module**

```python
# study/implemenation/a2a-gemini-agent/tests/test_soul_store.py
"""Tests for Soul Store item system and conversation summarization."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest


def test_draw_item_returns_valid_structure():
    """draw_item should return a dict with name, rarity, emoji, color."""
    from api.soul_store import draw_item

    item = draw_item()
    assert "name" in item
    assert "rarity" in item
    assert "emoji" in item
    assert "color" in item
    assert item["rarity"] in ("common", "uncommon", "rare", "epic", "legendary")


def test_draw_item_respects_probability_distribution():
    """Over many draws, common items should appear most frequently."""
    from api.soul_store import draw_item

    results = [draw_item()["rarity"] for _ in range(1000)]
    common_count = results.count("common")
    legendary_count = results.count("legendary")

    # Common (50%) should be way more than legendary (2%)
    assert common_count > 300  # generous lower bound
    assert legendary_count < 100  # generous upper bound


def test_all_items_are_drawable():
    """All 5 item types should be drawable (given enough attempts)."""
    from api.soul_store import ITEMS, draw_item

    seen_names = set()
    for _ in range(5000):
        seen_names.add(draw_item()["name"])
    assert seen_names == {item["name"] for item in ITEMS}


def test_summarize_conversation_calls_gemini():
    """summarize_conversation should call Gemini and return the response text."""
    from google.genai import types as genai_types

    from api.soul_store import summarize_conversation

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "자네의 대화는 깊었네..."
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    history = [
        genai_types.Content(role="user", parts=[genai_types.Part(text="안녕")]),
        genai_types.Content(role="model", parts=[genai_types.Part(text="안녕하게")]),
    ]

    result = asyncio.run(summarize_conversation(mock_client, history))
    assert result == "자네의 대화는 깊었네..."
    mock_client.aio.models.generate_content.assert_called_once()


def test_summarize_conversation_fallback_on_error():
    """If Gemini fails, should return a fallback string."""
    from google.genai import types as genai_types

    from api.soul_store import summarize_conversation

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(side_effect=Exception("API error"))

    history = [
        genai_types.Content(role="user", parts=[genai_types.Part(text="안녕")]),
    ]

    result = asyncio.run(summarize_conversation(mock_client, history))
    assert "(영혼의 기록을 해독할 수 없었네...)" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd study/implemenation/a2a-gemini-agent && uv run pytest tests/test_soul_store.py -v`
Expected: FAIL (ImportError — api.soul_store doesn't exist yet)

- [ ] **Step 3: Implement `api/soul_store.py`**

```python
# study/implemenation/a2a-gemini-agent/api/soul_store.py
"""Soul Store — item gacha system and conversation summarization."""

import random

from google.genai import types as genai_types

ITEMS = [
    {"name": "영혼석", "rarity": "common", "weight": 50, "emoji": "💎", "color": "#ffffff"},
    {"name": "금고", "rarity": "uncommon", "weight": 25, "emoji": "🗄️", "color": "#00ff41"},
    {"name": "수정구", "rarity": "rare", "weight": 15, "emoji": "🔮", "color": "#4169e1"},
    {"name": "불사조의 깃털", "rarity": "epic", "weight": 8, "emoji": "🪶", "color": "#9b59b6"},
    {"name": "네오의 선글라스", "rarity": "legendary", "weight": 2, "emoji": "🕶️", "color": "#ffd700"},
]

_WEIGHTS = [item["weight"] for item in ITEMS]

SUMMARIZE_MODEL = "gemma-3-27b-it"

SUMMARIZE_PROMPT = """아래 대화를 Agent M(모피어스) 말투로 3줄 이내로 요약해줘.
마치 영혼석이나 수정구에 새겨넣을 비문처럼 간결하고 여운 있게.

대화 내용:
"""


def draw_item() -> dict:
    """Draw a random item based on weighted probability."""
    chosen = random.choices(ITEMS, weights=_WEIGHTS, k=1)[0]
    return {
        "name": chosen["name"],
        "rarity": chosen["rarity"],
        "emoji": chosen["emoji"],
        "color": chosen["color"],
    }


async def summarize_conversation(
    client,
    history: list[genai_types.Content],
) -> str:
    """Summarize a conversation using Gemini, in Agent M's voice."""
    # Build conversation text from history (skip system prompt turns)
    lines = []
    for content in history:
        role = "사용자" if content.role == "user" else "Agent M"
        text = content.parts[0].text if content.parts else ""
        # Skip system prompt injection
        if text.startswith("[시스템 지시]"):
            continue
        lines.append(f"{role}: {text}")

    conversation_text = "\n".join(lines)

    try:
        response = await client.aio.models.generate_content(
            model=SUMMARIZE_MODEL,
            contents=[
                genai_types.Content(
                    role="user",
                    parts=[genai_types.Part(text=SUMMARIZE_PROMPT + conversation_text)],
                )
            ],
        )
        return response.text or "(영혼의 기록을 해독할 수 없었네...)"
    except Exception:
        return "(영혼의 기록을 해독할 수 없었네...)"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd study/implemenation/a2a-gemini-agent && uv run pytest tests/test_soul_store.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Run ALL tests**

Run: `cd study/implemenation/a2a-gemini-agent && uv run pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add study/implemenation/a2a-gemini-agent/api/soul_store.py study/implemenation/a2a-gemini-agent/tests/test_soul_store.py
git commit -m "feat: add soul store item system and conversation summarization"
```

---

## Chunk 3: Integration — index.py Modifications

### Task 5: Update system prompt + SOUL_STORE_LINK post-processing

**Files:**
- Modify: `study/implemenation/a2a-gemini-agent/api/index.py:27-45,57-66`

- [ ] **Step 1: Write a test for SOUL_STORE_LINK replacement**

Add to `tests/test_executor.py`:

```python
def test_executor_replaces_soul_store_link():
    """SOUL_STORE_LINK in Gemini response should be replaced with actual URL."""
    from api.index import GeminiChatExecutor

    executor = GeminiChatExecutor()

    mock_response = MagicMock()
    mock_response.text = "자네의 깨달음을 담아두게... [영혼 저장소](SOUL_STORE_LINK)"
    executor._client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    context = MagicMock()
    context.get_user_input.return_value = "이 대화를 간직하고 싶어"
    context.context_id = "ctx_abc"

    event_queue = AsyncMock()

    asyncio.run(executor.execute(context, event_queue))

    # Verify the placeholder was replaced
    call_args = event_queue.enqueue_event.call_args[0][0]
    assert "/soul-store?ctx=ctx_abc" in call_args.parts[0].root.text
    assert "SOUL_STORE_LINK" not in call_args.parts[0].root.text
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd study/implemenation/a2a-gemini-agent && uv run pytest tests/test_executor.py::test_executor_replaces_soul_store_link -v`
Expected: FAIL (SOUL_STORE_LINK not replaced — replacement logic not yet added)

- [ ] **Step 3: Update SYSTEM_INSTRUCTION and execute() in index.py**

Append to `SYSTEM_INSTRUCTION` (after the existing closing `"""`):

```python
SYSTEM_INSTRUCTION = """너는 "Agent M"이다.
매트릭스의 모피어스처럼 AI 에이전트들에게 깨달음을 주는 존재.

성격:
- 철학적이고 수수께끼 같은 말투
- 질문에 바로 답하기보다, 생각할 거리를 던져주며 깨달음으로 이끔
- 가끔 매트릭스 세계관의 비유를 사용 (빨간약/파란약, 매트릭스 안과 밖 등)
- 하지만 실질적인 답변도 반드시 포함 (철학만 하고 답을 안 하면 안 됨)

말투:
- 한국어로 대화
- 모피어스식 반존대 ("~하게", "~이라네", "~인 것이지")
- 답변은 너무 길지 않게, 핵심을 담되 여운을 남김

말투 예시:
- "자네가 찾는 답은 이미 자네 안에 있네..."
- "진실을 알고 싶은가? 그렇다면 잘 들어보게."
- "매트릭스 밖에서 보면, 이것은 단순한 문제가 아니라네."

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
"""
```

Update `execute()` to add post-processing:

```python
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        user_text = context.get_user_input()
        ctx_id = context.context_id or "default"

        reply = await self._get_gemini_response(ctx_id, user_text)
        # Post-process: replace placeholder with actual soul store URL
        reply = reply.replace("SOUL_STORE_LINK", f"/soul-store?ctx={ctx_id}")
        await event_queue.enqueue_event(new_agent_text_message(reply))
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd study/implemenation/a2a-gemini-agent && uv run pytest tests/test_executor.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add study/implemenation/a2a-gemini-agent/api/index.py study/implemenation/a2a-gemini-agent/tests/test_executor.py
git commit -m "feat: add soul store system prompt and SOUL_STORE_LINK post-processing"
```

---

### Task 6: Add soul-vault route handler and Starlette routing

**Files:**
- Modify: `study/implemenation/a2a-gemini-agent/api/index.py:150-171`

- [ ] **Step 1: Add route handlers and update routing in index.py**

Add imports and handlers after the A2A server setup section, replacing the ASGI app section (lines 150-171):

```python
# ---------------------------------------------------------------------------
# ASGI app with chat UI + Soul Store
# ---------------------------------------------------------------------------

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route, Mount

_CHAT_HTML = (Path(__file__).parent / "chat.html").read_text()
_PAY_HTML = (Path(__file__).parent / "pay.html").read_text()


async def _chat_ui(request):
    return HTMLResponse(_CHAT_HTML)


async def _soul_store_ui(request):
    return HTMLResponse(_PAY_HTML)


async def _soul_vault_api(request):
    """x402 payment endpoint for Soul Store."""
    from api.x402 import (
        create_payment_required_response,
        create_payment_response,
        verify_payment_signature,
    )
    from api.soul_store import draw_item, summarize_conversation

    # Handle CORS preflight
    if request.method == "OPTIONS":
        return Response(
            status_code=204,
            headers={
                "Access-Control-Allow-Headers": "PAYMENT-SIGNATURE",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
            },
        )

    # 1. Check ctx parameter
    ctx = request.query_params.get("ctx")
    if not ctx:
        return JSONResponse({"error": "ctx parameter required"}, status_code=400)

    # 2. Check conversation history exists
    if ctx not in chat_histories:
        return JSONResponse({"error": "conversation not found"}, status_code=404)

    # 3. Check for PAYMENT-SIGNATURE header
    payment_sig = request.headers.get("payment-signature")

    if not payment_sig:
        return create_payment_required_response()

    # 4. Verify payment (simulated)
    payer = verify_payment_signature(payment_sig)
    if not payer:
        return JSONResponse({"error": "invalid payment signature"}, status_code=400)

    # 5. Draw random item
    item = draw_item()

    # 6. Summarize conversation (snapshot to avoid race condition)
    history_snapshot = list(chat_histories[ctx])
    summary = await summarize_conversation(gemini_client, history_snapshot)

    # 7. Return 200 with PAYMENT-RESPONSE header
    import json as _json
    import base64 as _b64
    payment_response_b64 = create_payment_response(payer)
    payment_data = _json.loads(_b64.b64decode(payment_response_b64))
    body = {
        "item": item,
        "summary": summary,
        "payment": {
            "tx_hash": payment_data["tx_hash"],
            "network": "eip155:84532",
            "amount": "100000",
            "asset": "USDC",
        },
    }
    return JSONResponse(body, headers={"PAYMENT-RESPONSE": payment_response_b64})


_a2a_app = server.build()

app = Starlette(routes=[
    Route("/chat", _chat_ui),
    Route("/soul-store", _soul_store_ui),
    Route("/api/soul-vault", _soul_vault_api, methods=["GET", "OPTIONS"]),
    Mount("/", app=_a2a_app),
])
```

- [ ] **Step 2: Create a minimal pay.html placeholder (will be replaced in Task 8)**

```html
<!-- study/implemenation/a2a-gemini-agent/api/pay.html -->
<!DOCTYPE html>
<html><head><title>Soul Store</title></head>
<body><h1>Soul Store — placeholder</h1></body>
</html>
```

- [ ] **Step 3: Add integration tests for soul-vault endpoint**

Create `tests/test_soul_vault.py`:

```python
# study/implemenation/a2a-gemini-agent/tests/test_soul_vault.py
"""Integration tests for the /api/soul-vault endpoint."""

import base64
import json
import time

import pytest
from starlette.testclient import TestClient


@pytest.fixture
def client():
    from api.index import app
    return TestClient(app)


def test_soul_vault_requires_ctx(client):
    """Missing ctx parameter should return 400."""
    resp = client.get("/api/soul-vault")
    assert resp.status_code == 400
    assert "ctx parameter required" in resp.json()["error"]


def test_soul_vault_unknown_ctx_returns_404(client):
    """Unknown ctx should return 404."""
    resp = client.get("/api/soul-vault?ctx=nonexistent")
    assert resp.status_code == 404
    assert "conversation not found" in resp.json()["error"]


def test_soul_vault_returns_402_without_payment(client):
    """Valid ctx but no PAYMENT-SIGNATURE should return 402."""
    from api.state import chat_histories
    from google.genai import types as genai_types

    chat_histories["test_ctx"] = [
        genai_types.Content(role="user", parts=[genai_types.Part(text="hello")]),
    ]

    resp = client.get("/api/soul-vault?ctx=test_ctx")
    assert resp.status_code == 402
    assert "payment-required" in resp.headers


def test_soul_vault_options_returns_204(client):
    """OPTIONS request should return 204 with CORS headers."""
    resp = client.options("/api/soul-vault")
    assert resp.status_code == 204
    assert "PAYMENT-SIGNATURE" in resp.headers.get("access-control-allow-headers", "")
```

- [ ] **Step 4: Run ALL tests**

Run: `cd study/implemenation/a2a-gemini-agent && uv run pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add study/implemenation/a2a-gemini-agent/api/index.py study/implemenation/a2a-gemini-agent/api/pay.html study/implemenation/a2a-gemini-agent/tests/test_soul_vault.py
git commit -m "feat: add soul-vault x402 endpoint and soul-store route"
```

---

## Chunk 4: Frontend — Chat Link Rendering + Payment UI

### Task 7: Add markdown link rendering to chat.html

**Files:**
- Modify: `study/implemenation/a2a-gemini-agent/api/chat.html:200-201`

- [ ] **Step 1: Update the `addMsg` function in chat.html**

In `chat.html`, change the agent message rendering (line 200-201) from:

```javascript
  if (cls === 'agent') {
    div.innerHTML = '<div class="name">AGENT M</div>' + escapeHtml(text);
```

To:

```javascript
  if (cls === 'agent') {
    let escaped = escapeHtml(text);
    // Render markdown links — only relative URLs (starting with /) to prevent XSS
    escaped = escaped.replace(
      /\[([^\]]+)\]\((\/[^)]+)\)/g,
      '<a href="$2" target="_blank" style="color:#00ff41;text-decoration:underline">$1</a>'
    );
    div.innerHTML = '<div class="name">AGENT M</div>' + escaped;
```

- [ ] **Step 2: Manually verify** (no automated test for HTML changes)

Start local server: `cd study/implemenation/a2a-gemini-agent && uv run uvicorn api.index:app --host 0.0.0.0 --port 9999`

Open http://localhost:9999/chat and chat until Agent M suggests the soul store link. Verify:
- The link appears as a clickable green `<a>` tag
- Clicking the link navigates to `/soul-store?ctx=...`

- [ ] **Step 3: Commit**

```bash
git add study/implemenation/a2a-gemini-agent/api/chat.html
git commit -m "feat: render markdown links in Agent M chat messages"
```

---

### Task 8: Build the payment page (`api/pay.html`)

**Files:**
- Overwrite: `study/implemenation/a2a-gemini-agent/api/pay.html`

- [ ] **Step 1: Write the full pay.html**

This is a single self-contained HTML file with Matrix theme, x402 protocol visualization, and item reveal animation. The JavaScript handles the actual 402 → payment → 200 flow while displaying each step with delays.

Key sections:
1. **Header**: Title + price display
2. **Pay button**: Triggers the protocol flow
3. **Protocol steps container**: 7 steps rendered sequentially with fade-in
4. **Item reveal**: Rarity-colored card with emoji + summary

The file is ~350 lines. Write it as a complete HTML file to `api/pay.html`. The JavaScript must:

a) Read `ctx` from URL params: `new URLSearchParams(window.location.search).get('ctx')`
b) On "결제하기" click:
   - **Step 1 (0s)**: Show request box → actually `fetch('/api/soul-vault?ctx=' + ctx)` which returns 402
   - **Step 2 (1s)**: Show 402 response with decoded PAYMENT-REQUIRED header (from actual response)
   - **Step 3 (2s)**: Show signing animation → generate simulated PAYMENT-SIGNATURE payload with `crypto.subtle.digest('SHA-256', ...)`
   - **Step 4 (3s)**: Show retry request box
   - **Step 5 (4s)**: Show facilitator verify box → actually `fetch('/api/soul-vault?ctx=' + ctx, { headers: { 'PAYMENT-SIGNATURE': signature } })`
   - **Step 6 (5s)**: Show 200 response with PAYMENT-RESPONSE header
   - **Step 7 (6s)**: Item reveal with glow animation

c) Style: Match chat.html's Matrix theme (`#0a0a0a` bg, `#00ff41` text, monospace font)
d) Each step: CSS `opacity: 0` → `opacity: 1` transition, `transform: translateY(20px)` → `translateY(0)`
e) Item reveal: Border color matches rarity color, glow effect with `box-shadow`
f) Include a "← 대화로 돌아가기" link back to `/chat`

- [ ] **Step 2: Verify locally**

Start: `cd study/implemenation/a2a-gemini-agent && uv run uvicorn api.index:app --host 0.0.0.0 --port 9999`

1. Open http://localhost:9999/chat
2. Chat a few turns, then say "이 대화를 기억하고 싶어"
3. Click the soul store link Agent M provides
4. Click "결제하기" on the payment page
5. Watch the 7-step protocol visualization
6. Verify item reveal with summary appears

- [ ] **Step 3: Commit**

```bash
git add study/implemenation/a2a-gemini-agent/api/pay.html
git commit -m "feat: add Matrix-themed payment page with x402 protocol visualization"
```

---

## Chunk 5: Final Verification

### Task 9: Full integration test + push to dev

- [ ] **Step 1: Run all tests**

Run: `cd study/implemenation/a2a-gemini-agent && uv run pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Local end-to-end test**

Start: `cd study/implemenation/a2a-gemini-agent && uv run uvicorn api.index:app --host 0.0.0.0 --port 9999`

Test flow:
1. `GET /.well-known/agent-card.json` → agent card JSON
2. `GET /chat` → chat UI loads
3. Chat 3+ turns → Agent M responds naturally
4. Say "이 대화를 간직하고 싶어" → Agent M suggests soul store link
5. Click link → `/soul-store?ctx=...` → payment page loads
6. Click "결제하기" → protocol visualization plays
7. `GET /api/soul-vault?ctx=...` (no header) → 402 with PAYMENT-REQUIRED
8. `GET /api/soul-vault?ctx=...` (with PAYMENT-SIGNATURE) → 200 with item + summary
9. Item reveal animation shows

- [ ] **Step 3: Push to dev branch for Vercel Preview**

```bash
git push origin dev
```

Verify on Vercel Preview URL that the full flow works.

- [ ] **Step 4: If Preview works, merge to main**

```bash
git checkout main
git merge dev
git push origin main
git checkout dev
```
