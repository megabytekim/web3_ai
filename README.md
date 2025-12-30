# Web3 AI Agents

Claude Code 플러그인 시스템을 활용한 전문화된 AI 에이전트 컬렉션입니다.

## 개요

이 프로젝트는 [wshobson/agents](https://github.com/wshobson/agents) 저장소의 아키텍처 스타일을 따라 구현된 전문화된 AI 에이전트들을 포함합니다.

## 에이전트 목록

### 1. Web3 Agent (X402 & Ethereum)
**파일**: `plugins/web3-agent/agents/x402-ethereum-agent.md`

X402 프로토콜과 Ethereum 생태계 개발에 특화된 에이전트입니다.

**주요 기능**:
- X402 프로토콜 구현 및 표준 준수
- Ethereum 스마트 컨트랙트 개발 (Solidity, ERC 표준)
- Layer 2 솔루션: Polygon, Arbitrum, Optimism, Base, zkSync
- DeFi 프로토콜 통합: Uniswap, Aave, Compound
- Web3 프론트엔드 개발: Wagmi, Viem, RainbowKit
- NFT 및 디지털 자산 플랫폼
- 계정 추상화 (ERC-4337) 및 스마트 월렛

**사용 예시**:
```
"X402 토큰 표준을 구현하고 거버넌스와 스테이킹 메커니즘을 추가해줘"
"Ethereum과 X402 프로토콜 간의 크로스체인 브릿지를 만들어줘"
```

### 2. A2A Agent (Agent-to-Agent Communication)
**파일**: `plugins/ai-agent/agents/a2a-agent.md`

자율 멀티 에이전트 시스템 구축을 위한 에이전트 간 통신 전문가입니다.

**주요 기능**:
- A2A 통신 프로토콜 설계 및 구현
- 멀티 에이전트 시스템 아키텍처
- 에이전트 조정 및 협업
- 메시지 큐 및 이벤트 시스템 (Kafka, RabbitMQ)
- 분산 시스템 관찰성 및 모니터링
- 보안 및 접근 제어
- Kubernetes 기반 에이전트 배포

**사용 예시**:
```
"자율 트레이딩 에이전트들을 조정하기 위한 A2A 프로토콜을 설계해줘"
"우선순위 스케줄링이 있는 멀티 에이전트 태스크 큐를 구현해줘"
```

## 설치 및 사용

### 1. Claude Code 설정

이 에이전트들은 Claude Code의 플러그인 시스템을 사용합니다. 프로젝트 루트에서 Claude Code를 실행하면 자동으로 `.claude-plugin/marketplace.json` 파일을 감지합니다.

### 2. 에이전트 호출

Claude Code 대화에서 에이전트를 직접 호출할 수 있습니다:

```
"x402-ethereum-agent를 사용해서 DeFi 프로토콜을 만들어줘"
"a2a-agent로 멀티 에이전트 시스템을 설계해줘"
```

또는 Task 도구를 사용하여 특정 에이전트를 실행:

```
Task(subagent_type="x402-ethereum-agent", prompt="...")
```

## 프로젝트 구조

```
web3_ai/
├── .claude-plugin/
│   └── marketplace.json          # 플러그인 레지스트리
├── plugins/
│   ├── web3-agent/
│   │   └── agents/
│   │       └── x402-ethereum-agent.md
│   └── ai-agent/
│       └── agents/
│           └── a2a-agent.md
└── README.md
```

## 에이전트 모델 설정

모든 에이전트는 `opus` 모델을 사용하도록 설정되어 있습니다. 이는 복잡한 작업에 최적화된 설정입니다.

필요에 따라 각 에이전트의 마크다운 파일에서 `model` 필드를 변경할 수 있습니다:
- `opus`: 가장 강력한 모델 (복잡한 작업, 아키텍처, 보안)
- `sonnet`: 일반 개발 작업에 적합
- `haiku`: 빠르고 간단한 작업에 적합

## 커스터마이징

### 새로운 에이전트 추가

1. 새 플러그인 디렉토리 생성:
   ```bash
   mkdir -p plugins/your-agent/agents
   ```

2. 에이전트 마크다운 파일 생성:
   ```markdown
   ---
   name: your-agent
   description: Agent description here
   model: opus
   ---

   # Your agent content...
   ```

3. `marketplace.json`에 플러그인 등록:
   ```json
   {
     "name": "your-agent",
     "source": "./plugins/your-agent",
     "agents": ["./agents/your-agent.md"],
     ...
   }
   ```

## 참조

- 원본 아키텍처: [wshobson/agents](https://github.com/wshobson/agents)
- Claude Code 문서: [Claude Code Documentation](https://docs.anthropic.com/claude-code)

## 라이선스

MIT License

## 기여

이슈와 PR은 언제나 환영합니다!
