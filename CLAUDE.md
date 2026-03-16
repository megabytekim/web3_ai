# Web3 AI Study - Claude Code 가이드

## Week 6 데모 실행

### 가상환경 설정

데모 실행 전 반드시 가상환경을 활성화하세요.

```bash
cd study/week-6
source venv/bin/activate
```

가상환경이 없는 경우 생성:

```bash
cd study/week-6
python -m venv venv
source venv/bin/activate
pip install flask httpx pytest
```

### 데모 실행

**A2A + AP2:**
```bash
cd study/week-6/demos/a2a-ap2
python merchant_agent.py &   # 서버 (백그라운드)
python client_agent.py       # 클라이언트
```

**UCP:**
```bash
cd study/week-6/demos/ucp
python merchant_server.py &  # 서버 (백그라운드)
python client_demo.py        # 클라이언트
```

**x402:**
```bash
cd study/week-6/demos/x402
python server.py &           # 서버 (백그라운드)
python client.py             # 클라이언트
```

### 테스트 실행

```bash
cd study/week-6/demos
pytest -v
```

## A2A Gemini Agent 개발 워크플로우

### 브랜치 전략

- `main` → **Production** (`a2a-gemini-agent.vercel.app`)
- `dev` → **Preview** (Vercel이 자동 생성하는 Preview URL)

### 개발 흐름

```bash
# 1. dev 브랜치에서 작업
git checkout dev

# 2. 코드 수정 후 push → Vercel Preview 자동 배포
git add <파일>
git commit -m "feat: 어쩌구"
git push

# 3. Preview URL/chat 에서 테스트

# 4. 검증 완료 → main에 merge → Production 자동 배포
git checkout main
git merge dev
git push

# 5. 다시 dev로 돌아와서 계속 개발
git checkout dev
```

### 프로젝트 경로

- 코드: `study/implemenation/a2a-gemini-agent/`
- Vercel Root Directory: `study/implemenation/a2a-gemini-agent`
- 로컬 실행: `uv run uvicorn api.index:app --host 0.0.0.0 --port 9999`
