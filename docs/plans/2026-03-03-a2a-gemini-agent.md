# A2A Gemini Chat Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Gemini-powered chat agent accessible via the A2A protocol, deployed on Vercel.

**Architecture:** Single ASGI entry point using `a2a-sdk`'s `A2AStarletteApplication` for protocol handling. A `GeminiChatExecutor` maintains per-context chat history and calls Gemini's async API. Deployed as a Vercel serverless function.

**Tech Stack:** Python 3.12, a2a-sdk (v0.3.x), google-genai, uv, Vercel

---

### Task 1: Project scaffold

**Files:**
- Create: `study/implemenation/a2a-gemini-agent/pyproject.toml`
- Create: `study/implemenation/a2a-gemini-agent/.python-version`
- Create: `study/implemenation/a2a-gemini-agent/vercel.json`

**Step 1: Create project directory and init with uv**

```bash
mkdir -p study/implemenation/a2a-gemini-agent/api
cd study/implemenation/a2a-gemini-agent
uv init --no-readme
```

**Step 2: Replace pyproject.toml with correct config**

```toml
[project]
name = "a2a-gemini-agent"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "a2a-sdk[http-server]",
    "google-genai",
]
```

**Step 3: Add dependencies with uv**

```bash
cd study/implemenation/a2a-gemini-agent
uv add "a2a-sdk[http-server]" google-genai
```

Expected: `uv.lock` generated, dependencies resolved.

**Step 4: Create .python-version**

File: `.python-version`
```
3.12
```

**Step 5: Create vercel.json**

```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

**Step 6: Delete the auto-generated hello.py from uv init**

```bash
rm -f study/implemenation/a2a-gemini-agent/hello.py
```

**Step 7: Commit**

```bash
git add study/implemenation/a2a-gemini-agent/
git commit -m "chore: scaffold a2a-gemini-agent project with uv"
```

---

### Task 2: Write the agent executor with test

**Files:**
- Create: `study/implemenation/a2a-gemini-agent/api/index.py`
- Create: `study/implemenation/a2a-gemini-agent/tests/test_executor.py`

**Step 1: Write the failing test**

File: `tests/test_executor.py`

```python
"""Tests for GeminiChatExecutor."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_executor_extracts_text_and_calls_gemini():
    """Executor should extract user text, call Gemini, and enqueue response."""
    from api.index import GeminiChatExecutor

    executor = GeminiChatExecutor()

    # Mock context
    context = MagicMock()
    context.get_user_input.return_value = "Hello, who are you?"
    context.context_id = "ctx_123"

    # Mock event queue
    event_queue = AsyncMock()

    # Mock Gemini response
    mock_response = MagicMock()
    mock_response.text = "I'm a Gemini-powered chat agent!"

    with patch.object(executor, "_get_gemini_response", new_callable=AsyncMock) as mock_gemini:
        mock_gemini.return_value = "I'm a Gemini-powered chat agent!"
        asyncio.run(executor.execute(context, event_queue))

    event_queue.enqueue_event.assert_called_once()
    call_args = event_queue.enqueue_event.call_args[0][0]
    assert call_args.parts[0].text == "I'm a Gemini-powered chat agent!"


def test_executor_maintains_separate_contexts():
    """Different contextIds should have separate chat histories."""
    from api.index import GeminiChatExecutor

    executor = GeminiChatExecutor()
    assert executor._chat_histories == {}

    # Simulate adding history for two contexts
    executor._chat_histories["ctx_1"] = [{"role": "user", "text": "hi"}]
    executor._chat_histories["ctx_2"] = [{"role": "user", "text": "hello"}]

    assert len(executor._chat_histories) == 2
    assert executor._chat_histories["ctx_1"] != executor._chat_histories["ctx_2"]


def test_cancel_raises():
    """Cancel should raise an exception (not supported)."""
    from api.index import GeminiChatExecutor

    executor = GeminiChatExecutor()
    context = MagicMock()
    event_queue = AsyncMock()

    with pytest.raises(Exception, match="cancel not supported"):
        asyncio.run(executor.cancel(context, event_queue))
```

**Step 2: Run test to verify it fails**

```bash
cd study/implemenation/a2a-gemini-agent
uv run pytest tests/test_executor.py -v
```

Expected: FAIL — `api/index.py` does not exist yet.

**Step 3: Write the main application**

File: `api/index.py`

```python
"""A2A Gemini Chat Agent — ASGI entry point for Vercel."""

import os

from google import genai
from google.genai import types as genai_types

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.utils import new_agent_text_message


# ---------------------------------------------------------------------------
# Gemini Chat Executor
# ---------------------------------------------------------------------------

class GeminiChatExecutor(AgentExecutor):
    """A2A agent that chats using Google Gemini with multi-turn history."""

    MODEL = "gemini-2.5-flash"

    def __init__(self) -> None:
        self._client = genai.Client()
        self._chat_histories: dict[str, list[genai_types.Content]] = {}

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        user_text = context.get_user_input()
        ctx_id = context.context_id or "default"

        reply = await self._get_gemini_response(ctx_id, user_text)
        await event_queue.enqueue_event(new_agent_text_message(reply))

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        raise Exception("cancel not supported")

    async def _get_gemini_response(self, ctx_id: str, user_text: str) -> str:
        """Send message to Gemini with conversation history."""
        if ctx_id not in self._chat_histories:
            self._chat_histories[ctx_id] = []

        history = self._chat_histories[ctx_id]
        history.append(
            genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=user_text)],
            )
        )

        response = await self._client.aio.models.generate_content(
            model=self.MODEL,
            contents=history,
        )

        assistant_text = response.text or "(no response)"
        history.append(
            genai_types.Content(
                role="model",
                parts=[genai_types.Part(text=assistant_text)],
            )
        )
        return assistant_text


# ---------------------------------------------------------------------------
# A2A Server Setup
# ---------------------------------------------------------------------------

skill = AgentSkill(
    id="chat",
    name="General Chat",
    description="General-purpose conversation powered by Google Gemini",
    tags=["chat", "gemini", "conversation"],
    examples=["Hello!", "Tell me about A2A protocol", "What can you do?"],
)

agent_card = AgentCard(
    name="Gemini Chat Agent",
    description="A2A agent that chats using Google Gemini with multi-turn context",
    url=os.environ.get("AGENT_URL", "http://localhost:9999/"),
    version="0.1.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill],
)

request_handler = DefaultRequestHandler(
    agent_executor=GeminiChatExecutor(),
    task_store=InMemoryTaskStore(),
)

server = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler,
)

app = server.build()
```

**Step 4: Run tests to verify they pass**

```bash
cd study/implemenation/a2a-gemini-agent
uv run pytest tests/test_executor.py -v
```

Expected: 3 tests PASS.

**Step 5: Commit**

```bash
git add study/implemenation/a2a-gemini-agent/api/index.py study/implemenation/a2a-gemini-agent/tests/
git commit -m "feat: add GeminiChatExecutor with A2A server setup"
```

---

### Task 3: Write a test client script

**Files:**
- Create: `study/implemenation/a2a-gemini-agent/test_client.py`

**Step 1: Write test client**

```python
"""Simple test client for the A2A Gemini Chat Agent."""

import httpx
import uuid
import json

AGENT_URL = "http://localhost:9999"


def main():
    client = httpx.Client(timeout=30.0)

    # Step 1: Discover agent
    print("=== Agent Discovery ===")
    resp = client.get(f"{AGENT_URL}/.well-known/agent.json")
    card = resp.json()
    print(f"Name: {card['name']}")
    print(f"Skills: {[s['name'] for s in card['skills']]}")

    # Step 2: Send first message
    context_id = f"ctx_{uuid.uuid4().hex[:8]}"
    print(f"\n=== Chat (context: {context_id}) ===")

    messages = [
        "Hello! What can you do?",
        "Tell me a short joke.",
        "What was my first message to you?",  # tests multi-turn memory
    ]

    for msg in messages:
        print(f"\nUser: {msg}")
        result = send_message(client, context_id, msg)
        if result:
            # Extract agent response from task artifacts or status
            print(f"Agent: {json.dumps(result, indent=2, ensure_ascii=False)}")


def send_message(client: httpx.Client, context_id: str, text: str) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "contextId": context_id,
                "parts": [{"kind": "text", "text": text}],
            }
        },
    }
    resp = client.post(
        f"{AGENT_URL}/",
        json=payload,
        headers={"Content-Type": "application/json"},
    )
    return resp.json()


if __name__ == "__main__":
    main()
```

**Step 2: Commit**

```bash
git add study/implemenation/a2a-gemini-agent/test_client.py
git commit -m "feat: add A2A test client script"
```

---

### Task 4: Local end-to-end test

**Step 1: Set Gemini API key**

```bash
export GEMINI_API_KEY="your-key-here"
```

**Step 2: Run the server locally**

```bash
cd study/implemenation/a2a-gemini-agent
uv run uvicorn api.index:app --host 0.0.0.0 --port 9999
```

Expected: Server starts, listening on port 9999.

**Step 3: Test agent card discovery (in another terminal)**

```bash
curl http://localhost:9999/.well-known/agent.json | python -m json.tool
```

Expected: Returns agent card JSON with name "Gemini Chat Agent".

**Step 4: Run the test client**

```bash
cd study/implemenation/a2a-gemini-agent
uv run python test_client.py
```

Expected: Three messages sent, Gemini responds to each, third response references the first message (multi-turn working).

**Step 5: Stop server and commit any fixes**

---

### Task 5: Deploy to Vercel

**Step 1: Ensure Vercel CLI is installed**

```bash
vercel --version
```

If not installed: `npm i -g vercel`

**Step 2: Create requirements.txt for Vercel**

Vercel's `@vercel/python` builder uses `requirements.txt` (not `pyproject.toml` via uv). Create one:

```bash
cd study/implemenation/a2a-gemini-agent
uv pip compile pyproject.toml -o requirements.txt
```

Alternatively, create manually:

```
a2a-sdk[http-server]
google-genai
```

**Step 3: Set environment variable in Vercel**

```bash
cd study/implemenation/a2a-gemini-agent
vercel env add GEMINI_API_KEY
```

Enter your Gemini API key when prompted. Select all environments (Production, Preview, Development).

**Step 4: Set AGENT_URL environment variable**

After first deployment, set `AGENT_URL` to your Vercel URL:

```bash
vercel env add AGENT_URL
# Enter: https://your-project.vercel.app/
```

**Step 5: Deploy**

```bash
cd study/implemenation/a2a-gemini-agent
vercel deploy
```

Expected: Deployment succeeds, returns a preview URL.

**Step 6: Test the deployment**

```bash
curl https://your-preview-url.vercel.app/.well-known/agent.json | python -m json.tool
```

Expected: Agent card returned.

**Step 7: Deploy to production**

```bash
vercel deploy --prod
```

**Step 8: Final commit**

```bash
git add study/implemenation/a2a-gemini-agent/requirements.txt
git commit -m "feat: add requirements.txt for Vercel deployment"
```

---

### Task 6: Add README

**Files:**
- Create: `study/implemenation/a2a-gemini-agent/README.md`

**Step 1: Write README**

```markdown
# A2A Gemini Chat Agent

A2A 프로토콜을 통해 접근 가능한 Gemini 기반 챗봇 에이전트.

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- `GEMINI_API_KEY` ([Google AI Studio](https://aistudio.google.com/)에서 발급)

### Local Development

```bash
export GEMINI_API_KEY="your-key"
uv run uvicorn api.index:app --host 0.0.0.0 --port 9999
```

### Test

```bash
# Unit tests
uv run pytest tests/ -v

# Manual test (서버 실행 후)
uv run python test_client.py
```

### Deploy to Vercel

```bash
vercel env add GEMINI_API_KEY
vercel deploy --prod
```

## A2A Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/.well-known/agent.json` | GET | Agent Card (에이전트 발견) |
| `/` | POST | JSON-RPC (message/send, tasks/get 등) |

## Architecture

- **a2a-sdk**: A2A 프로토콜 처리 (Agent Card, JSON-RPC)
- **google-genai**: Gemini API 호출 (gemini-2.5-flash)
- **Starlette**: ASGI 서버 (a2a-sdk 내장)
- Multi-turn 대화: contextId 기반 in-memory 히스토리
```

**Step 2: Commit**

```bash
git add study/implemenation/a2a-gemini-agent/README.md
git commit -m "docs: add README for a2a-gemini-agent"
```
