# Web3 AI Agents Documentation

이 디렉토리는 Web3 AI 에이전트 프로젝트의 문서를 포함합니다.

## 📚 문서 구조

```
docs/
├── README.md           # 이 파일
└── a2a/               # A2A Protocol 문서
    ├── a2a-protocol-overview.md
    ├── a2a-architecture.md
    ├── a2a-implementation-guide.md
    └── a2a-examples.md
```

## 📖 A2A Protocol 문서

### [A2A Protocol 디렉토리](./a2a/)

독립적인 AI 에이전트 시스템 간의 통신과 상호운용성을 위한 개방형 표준에 대한 포괄적인 가이드입니다.

#### 문서 목록

1. **[a2a-protocol-overview.md](./a2a/a2a-protocol-overview.md)** - 프로토콜 개요
   - A2A 프로토콜 소개 및 역사
   - 4가지 핵심 기능 (능력 발견, 작업 관리, 협업, UX 협상)
   - 기술적 기반 (HTTP, JSON-RPC, SSE, Protocol Buffers)
   - 파트너십 (50+ 기술 파트너)
   - 보안 및 SDK 정보

2. **[a2a-architecture.md](./a2a/a2a-architecture.md)** - 아키텍처 심층 분석
   - 3계층 아키텍처 상세 설명
   - Tasks, Messages, Agent Cards 구조
   - Task 라이프사이클 및 상태 전환
   - 통신 패턴 (동기/스트리밍/비동기)
   - 보안 아키텍처 (인증/권한 부여)
   - 멀티턴 상호작용 및 컨텍스트 관리

3. **[a2a-implementation-guide.md](./a2a/a2a-implementation-guide.md)** - 구현 가이드
   - SDK 설치 (Python, JavaScript, Go 등)
   - Agent Card 구현
   - 메시지 처리 (동기/스트리밍)
   - Task 관리 및 라이프사이클
   - Webhook 구현 및 보안
   - 테스팅 및 배포

4. **[a2a-examples.md](./a2a/a2a-examples.md)** - 10가지 실전 예제
   - 간단한 텍스트 대화
   - 파일 처리
   - 스트리밍 응답
   - 멀티턴 대화
   - 에이전트 간 협업
   - 복잡한 워크플로우

#### 학습 경로

**초급**: A2A 프로토콜 이해하기
1. [a2a-protocol-overview.md](./a2a/a2a-protocol-overview.md) 읽기
2. [a2a-examples.md](./a2a/a2a-examples.md)의 예제 1-3 실습

**중급**: 에이전트 구현하기
1. [a2a-architecture.md](./a2a/a2a-architecture.md) 학습
2. [a2a-implementation-guide.md](./a2a/a2a-implementation-guide.md) 따라하기
3. [a2a-examples.md](./a2a/a2a-examples.md)의 예제 4-7 실습

**고급**: 프로덕션 시스템 구축
1. [a2a-architecture.md](./a2a/a2a-architecture.md)의 보안 및 관찰성 섹션 심화 학습
2. [a2a-implementation-guide.md](./a2a/a2a-implementation-guide.md)의 배포 및 모니터링 구현
3. [a2a-examples.md](./a2a/a2a-examples.md)의 예제 8-10으로 복잡한 시스템 설계

## 🔗 외부 참고 자료

### A2A Protocol 공식 문서
- [A2A 공식 웹사이트](https://a2a-protocol.org/latest/)
- [A2A 전체 스펙](https://a2a-protocol.org/latest/specification/)
- [A2A GitHub 저장소](https://github.com/a2aproject/A2A)
- [A2A 샘플 코드](https://github.com/a2aproject/a2a-samples)

### 블로그 및 가이드
- [Google Developers Blog - A2A 발표](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
- [IBM A2A 가이드](https://www.ibm.com/think/topics/agent2agent-protocol)
- [DEV Community - A2A 완전 가이드](https://dev.to/czmilo/2025-complete-guide-agent2agent-a2a-protocol-the-new-standard-for-ai-agent-collaboration-1pph)

### SDK 문서
- Python SDK: `pip install a2a-sdk`
- JavaScript SDK: `npm install @a2a/sdk`
- Go SDK: `go get github.com/a2aproject/a2a-go`

## 🛠️ 프로젝트 에이전트

이 프로젝트에는 다음 에이전트들이 포함되어 있습니다:

### 1. X402-Ethereum Agent
**파일**: `plugins/web3-agent/agents/x402-ethereum-agent.md`

Web3 및 Ethereum 개발을 위한 전문 에이전트
- X402 프로토콜 구현
- Ethereum 스마트 컨트랙트 개발
- DeFi 프로토콜 통합
- NFT 플랫폼 개발
- Layer 2 솔루션

### 2. AI Agent
**파일**: `plugins/ai-agent/agents/ai-agent.md`

포괄적인 AI 에이전트 개발 전문가
- LLM 통합 (OpenAI, Anthropic, Google)
- 에이전트 프레임워크 (LangChain, CrewAI, AutoGPT)
- RAG (Retrieval Augmented Generation)
- 멀티 에이전트 시스템
- A2A Protocol 통신
- 툴 통합 및 Function Calling
- 메모리 및 컨텍스트 관리

## 📝 문서 기여

이 문서는 다음 소스를 바탕으로 작성되었습니다:
- A2A 공식 스펙 (v1.0 Draft)
- GitHub a2aproject/A2A 저장소
- 커뮤니티 가이드 및 블로그
- 최신 AI 에이전트 프레임워크 문서

문서의 개선 사항이나 오류를 발견하시면 이슈를 등록해주세요.

## 🔄 업데이트 내역

- **2025-12-30**: 초기 문서 세트 작성
  - A2A Protocol 문서 4개 추가 (Overview, Architecture, Implementation, Examples)
  - 문서를 `docs/a2a/` 디렉토리로 구조화
  - AI Agent를 A2A 특화에서 범용 AI 에이전트로 확장

## 📬 문의

문의사항이나 제안이 있으시면 프로젝트 이슈를 통해 연락주세요.
