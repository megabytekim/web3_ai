# A2A Gemini Chat Agent Design

## Overview

A2A 프로토콜을 통해 접근 가능한 Gemini 기반 챗봇 에이전트.
Vercel에 서버리스로 배포하며, `a2a-sdk`와 `google-genai`를 사용.

## Requirements

- A2A 프로토콜 v0.3.0 (a2a-sdk 지원 버전)
- Gemini API (`gemini-2.5-flash` 모델)
- Vercel 서버리스 배포
- Multi-turn 대화 지원 (contextId 기반, in-memory)
- uv 패키지 관리

## Architecture

```
Client (any A2A client)
    |
    v
Vercel Serverless Function (ASGI)
    |
    +-- GET /.well-known/agent-card.json  (a2a-sdk auto)
    |
    +-- POST /  (JSON-RPC)               (a2a-sdk handler)
         |
         v
    GeminiChatExecutor
         |
         +-- Chat history per contextId (in-memory dict)
         +-- Gemini API call (async, google-genai)
         +-- Response via EventQueue
```

## File Structure

```
study/implemenation/a2a-gemini-agent/
+-- api/
|   +-- index.py              # ASGI entry point
+-- pyproject.toml             # uv dependencies
+-- uv.lock                    # auto-generated
+-- vercel.json                # routing config
+-- .python-version            # 3.12
+-- README.md                  # usage/deploy guide
```

## Components

### GeminiChatExecutor (~40 lines)

- `AgentExecutor` 상속
- `execute()`: contextId로 Gemini 채팅 세션 조회/생성 -> 메시지 전송 -> 응답 enqueue
- `cancel()`: 미지원 예외
- 채팅 히스토리: `dict[str, Chat]` (contextId 기반)

### Agent Card

- name: "Gemini Chat Agent"
- skill: "chat" (general conversation)
- input/output modes: ["text/plain"]
- capabilities: streaming=False
- protocolVersion: "0.3.0"

### Dependencies

- `a2a-sdk[http-server]` - A2A protocol + Starlette server
- `google-genai` - Gemini API SDK

### Environment Variables

- `GEMINI_API_KEY` - Vercel Dashboard에서 설정

## Known Limitations

- In-memory 채팅 히스토리는 cold start시 초기화됨
- InMemoryTaskStore도 동일한 제약
- WebSocket/streaming 미지원 (서버리스 제약)
- 데모 수준에서는 문제없음

## Estimated Code

~100 lines total (single index.py file)
