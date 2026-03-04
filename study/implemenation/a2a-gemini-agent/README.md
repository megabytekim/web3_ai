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
