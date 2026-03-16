# A2A Gemini Chat Agent — Agent M

매트릭스의 모피어스처럼 깨달음을 주는 A2A 챗 에이전트 + x402 결제 기반 영혼 저장소.

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- `GEMINI_API_KEY` ([Google AI Studio](https://aistudio.google.com/)에서 발급)

### Local Development

```bash
cd study/implemenation/a2a-gemini-agent
export GEMINI_API_KEY="your-key"
uv run uvicorn api.index:app --host 0.0.0.0 --port 9999
```

브라우저에서:
- http://localhost:9999/chat — Agent M 채팅 UI
- http://localhost:9999/soul-store?ctx=xxx — 영혼 저장소 (결제 페이지)

### Tests

```bash
uv run pytest tests/ -v          # 전체 테스트 (22개)
uv run pytest tests/test_x402.py # x402 프로토콜만
uv run python test_client.py     # 수동 A2A 클라이언트 (서버 실행 후)
```

## Dev/Prod 워크플로우

```
main  → Production  (a2a-gemini-agent.vercel.app)
dev   → Preview     (Vercel이 자동 생성하는 Preview URL)
```

### 개발 흐름

```bash
# 1. dev 브랜치에서 작업
git checkout dev

# 2. 코드 수정 후 push → Vercel Preview 자동 배포
git add <파일>
git commit -m "feat: 어쩌구"
git push origin dev

# 3. Vercel Dashboard에서 Preview URL 확인 → /chat 에서 테스트

# 4. 검증 완료 → main에 merge
git checkout main
git merge dev
git push origin main

# 5. 다시 dev로 돌아와서 계속 개발
git checkout dev
```

### Vercel 설정

- **Root Directory**: `study/implemenation/a2a-gemini-agent`
- **Framework**: Other
- **Build**: `@vercel/python`
- **환경변수**: `GEMINI_API_KEY` (Production + Preview 모두 설정)

## 프로젝트 구조

```
api/
  index.py          ← A2A 에이전트 + Starlette 라우팅
  state.py          ← 공유 상태 (Gemini client, chat histories)
  x402.py           ← x402 V2 프로토콜 시뮬레이션
  soul_store.py     ← 아이템 뽑기 + Gemini 대화 요약
  chat.html         ← Agent M 채팅 UI (Matrix 테마)
  pay.html          ← 결제 페이지 + x402 프로토콜 시각화
tests/
  conftest.py       ← 공유 fixture (Gemini mock)
  test_executor.py  ← A2A executor 테스트
  test_x402.py      ← x402 프로토콜 테스트
  test_soul_store.py← 아이템/요약 테스트
  test_soul_vault.py← /api/soul-vault 통합 테스트
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | GET | Agent M 채팅 UI |
| `/soul-store?ctx=xxx` | GET | 영혼 저장소 결제 페이지 |
| `/api/soul-vault?ctx=xxx` | GET | x402 결제 엔드포인트 (402→200 flow) |
| `/.well-known/agent.json` | GET | A2A Agent Card |
| `/` | POST | A2A JSON-RPC (message/send) |

## 핵심 흐름

```
사용자 ─── /chat ───> Agent M
                        │
          "대화를 간직하고 싶어"
                        │
          Agent M: [영혼 저장소 링크]
                        │
사용자 ─── /soul-store ───> 결제 페이지
                        │
              x402 프로토콜 시각화
         (402 → 서명 → 200 + 아이템)
                        │
              🔮 랜덤 아이템 + 대화 요약
```

## 기술 스택

- **A2A SDK**: 에이전트 간 통신 프로토콜
- **google-genai**: Gemma 3 27B IT 모델 호출
- **x402 V2**: HTTP 402 기반 결제 프로토콜 (시뮬레이션)
- **Starlette**: ASGI 서버
- **Vercel**: 서버리스 배포
