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
