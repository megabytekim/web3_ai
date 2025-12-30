# Agent2Agent (A2A) Protocol - Overview

## 소개

Agent2Agent (A2A) Protocol은 독립적이고 잠재적으로 불투명한 AI 에이전트 시스템 간의 통신과 상호운용성을 촉진하기 위해 설계된 개방형 표준입니다.

## 핵심 정보

- **공식 사이트**: [a2a-protocol.org](https://a2a-protocol.org/latest/)
- **GitHub**: [github.com/google/a2a](https://github.com/google/a2a)
- **스펙 버전**: 0.3.0 (최신)
- **라이선스**: Apache 2.0
- **관리 주체**: Google / Linux Foundation
- **주요 기여자**: Google Cloud
- **프로토콜 유형**: Transport-agnostic (JSON-RPC 2.0, gRPC, REST-style HTTP+JSON)

## 출시 및 지원

### 출시 시기
- 2025년 4월, Google Cloud와 기술 파트너들이 주도하여 공개

### 파트너십
50개 이상의 기술 파트너가 지원 및 기여:

**기술 파트너**:
- Atlassian, Box, Cohere, Intuit
- Langchain, MongoDB, PayPal, Salesforce
- SAP, ServiceNow, UKG, Workday

**서비스 제공업체**:
- Accenture, BCG, Capgemini, Cognizant
- Deloitte, HCLTech, Infosys, KPMG
- McKinsey, PwC, TCS, Wipro

## 프로토콜의 목적

A2A 프로토콜은 다음을 가능하게 합니다:

1. **에이전트 간 직접 통신**: 서로 다른 프레임워크로 구축된 AI 에이전트들이 도구가 아닌 협력자로서 직접 통신
2. **보안 정보 교환**: 안전하게 정보를 교환하고 작업 조율
3. **플랫폼 독립성**: 다양한 엔터프라이즈 플랫폼 또는 애플리케이션 위에서 작동
4. **운영 불투명성 유지**: 내부 메모리나 독점 도구를 노출하지 않고 독립적으로 작동

## 4가지 핵심 기능

### 1. 능력 발견 (Capability Discovery)
에이전트는 JSON 형식의 "Agent Card"를 사용하여 자신의 능력을 광고할 수 있습니다. 클라이언트 에이전트는 이를 통해 작업을 수행할 수 있는 최적의 에이전트를 식별하고 A2A를 활용하여 원격 에이전트와 통신합니다.

### 2. 작업 관리 (Task Management)
클라이언트와 원격 에이전트 간의 통신은 작업 완료를 지향합니다. 에이전트는 최종 사용자 요청을 충족하기 위해 협력합니다. 프로토콜은 "task" 객체와 라이프사이클을 정의합니다.

### 3. 협업 (Collaboration)
에이전트는 컨텍스트, 응답, 아티팩트 또는 사용자 지시를 전달하기 위해 서로 메시지를 보낼 수 있습니다.

### 4. 사용자 경험 협상 (UX Negotiation)
각 부분은 지정된 콘텐츠 유형을 가지고 있어, 클라이언트와 원격 에이전트가 필요한 올바른 형식을 협상할 수 있습니다. 이는 사용자의 UI 기능(예: iframe, 비디오, 웹 폼 등)에 대한 명시적 협상을 포함합니다.

## 기술적 기반

A2A 프로토콜은 기존의 잘 이해된 표준을 재사용합니다:

- **HTTP/HTTPS**: 전송 프로토콜
- **JSON-RPC 2.0**: 원격 프로시저 호출
- **Server-Sent Events (SSE)**: 실시간 스트리밍
- **Protocol Buffers**: 정규 데이터 모델

## 보안 및 엔터프라이즈 고려사항

A2A 프로토콜은 엔터프라이즈급 보안 요구사항을 충족하도록 설계되었습니다.

### Transport 보안
- **필수 요구사항**: 프로덕션 환경에서는 **HTTPS 필수**
- **권장 사항**: TLS 1.3+ 사용 및 강력한 cipher suite 구성
- **서버 신원 확인**: 클라이언트는 TLS 인증서를 통해 A2A 서버 신원 검증 권장

### 인증 (Authentication)

A2A는 HTTP 전송 계층에서 신원 정보를 처리하며, JSON-RPC 페이로드 내부가 아닌 표준 웹 보안 방식을 따릅니다.

**인증 프로세스**:

1. **요구사항 발견**: 클라이언트가 Agent Card의 `authentication` 필드를 통해 필요한 인증 방식 확인
2. **자격증명 획득 (Out-of-Band)**: 클라이언트가 대역 외 프로세스를 통해 자격증명 획득 (예: API 키, OAuth 토큰)
3. **자격증명 전송**: HTTP 헤더에 자격증명 포함 (예: `Authorization`, `X-API-Key`)

**지원 인증 방식**:
- OAuth 2.0
- OpenID Connect
- API Keys
- Bearer Tokens
- Mutual TLS (mTLS)

### 서버 인증 책임

A2A 서버는 다음을 준수해야 합니다:

- **필수**: 제공된 HTTP 자격증명을 기반으로 모든 요청 인증
- **권장**: 인증 실패 시 표준 HTTP 상태 코드 사용 (`401 Unauthorized`, `403 Forbidden`)
- **권장**: `401` 응답에 관련 HTTP 헤더 포함 (예: `WWW-Authenticate`)
- **권장**: TLS 인증서를 통해 클라이언트의 webhook 서버 신원 검증

### 권한 부여 및 데이터 보호

- **권한 부여**: 작업 접근 권한 범위 세밀하게 지정
- **데이터 보안**: 데이터 접근 범위 제한 및 정보 유출 방지
- **개인정보 보호**: 민감한 정보를 위한 인증된 "확장" Agent Card 제공

### 관찰성

- **추적 (Tracing)**: 분산 시스템 추적 지원 (OpenTelemetry 호환)
- **모니터링 (Monitoring)**: 표준 관찰성 및 로깅 기능
- **감사 (Auditing)**: 모든 에이전트 상호작용에 대한 감사 로그

## Transport Layer 요구사항

A2A 통신의 기본 요구사항:

- **프로토콜**: HTTP(S) **필수**
- **에이전트 준수**: 3가지 핵심 트랜스포트 프로토콜 중 **최소 1개 구현 필수**
- **동등성**: 모든 지원 트랜스포트 프로토콜은 상태와 기능에서 동등
- **서비스 노출**: A2A 서버는 `AgentCard`의 URL을 통해 서비스 노출

## 프로토콜 바인딩

A2A는 여러 프로토콜 바인딩을 지원하여 다양한 환경에서 사용 가능:

1. **JSON-RPC 2.0 over HTTP/HTTPS**: 기본 바인딩, 가장 널리 사용됨
2. **gRPC**: 고성능 시나리오용, 효율적인 바이너리 프로토콜
3. **HTTP+JSON (REST-style)**: RESTful API 스타일

**중요**:
- 에이전트는 **최소 1개의 트랜스포트 프로토콜을 구현**해야 함
- 모든 바인딩은 "기능적 동등성"을 유지
- 일관된 오류 코드와 데이터 표현 제공

### 프로토콜 선택 가이드

| 프로토콜 | 사용 사례 | 장점 |
|---------|----------|------|
| JSON-RPC | 범용, 웹 호환성 | 간단, 디버깅 용이, 광범위한 지원 |
| gRPC | 고성능, 마이크로서비스 | 빠름, 타입 안전성, 스트리밍 최적화 |
| HTTP+JSON | REST 기반 시스템 | REST 표준 준수, 기존 인프라 활용 |

## Agent Card - 에이전트 발견

Agent Card는 에이전트의 능력, 엔드포인트, 보안 요구사항을 설명하는 JSON 매니페스트입니다. 이를 통해 에이전트들이 서로를 발견하고 이해할 수 있습니다.

### Agent Card 예제

```json
{
  "protocolVersion": "0.3.0",
  "name": "GeoSpatial Route Planner Agent",
  "description": "Provides advanced route planning, traffic analysis, and custom map generation services.",
  "url": "https://georoute-agent.example.com/a2a/v1",
  "preferredTransport": "JSONRPC",
  "additionalInterfaces": [
    {
      "url": "https://georoute-agent.example.com/a2a/v1",
      "transport": "JSONRPC"
    },
    {
      "url": "https://georoute-agent.example.com/a2a/grpc",
      "transport": "GRPC"
    },
    {
      "url": "https://georoute-agent.example.com/a2a/json",
      "transport": "HTTP+JSON"
    }
  ],
  "provider": {
    "organization": "Example Geo Services Inc.",
    "url": "https://www.examplegeoservices.com"
  },
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": false
  },
  "securitySchemes": {
    "google": {
      "type": "openIdConnect",
      "openIdConnectUrl": "https://accounts.google.com/.well-known/openid-configuration"
    }
  },
  "security": [
    {"google": ["openid", "profile", "email"]}
  ],
  "defaultInputModes": ["application/json", "text/plain"],
  "defaultOutputModes": ["application/json", "image/png"],
  "skills": [
    {
      "id": "route-optimizer-traffic",
      "name": "Traffic-Aware Route Optimizer",
      "description": "Calculates optimal driving routes considering real-time traffic conditions.",
      "tags": ["maps", "routing", "navigation", "directions", "traffic"],
      "examples": [
        "Plan a route from '1600 Amphitheatre Parkway, Mountain View, CA' to 'San Francisco International Airport' avoiding tolls."
      ],
      "inputModes": ["application/json", "text/plain"],
      "outputModes": ["application/json", "application/vnd.geo+json", "text/html"]
    }
  ]
}
```

### Agent Card 주요 필드

- **protocolVersion**: A2A 프로토콜 버전 (예: "0.3.0")
- **name**: 에이전트 이름
- **description**: 에이전트 설명
- **url**: 기본 엔드포인트 URL
- **preferredTransport**: 선호하는 트랜스포트 프로토콜
- **capabilities**: 에이전트 기능 (스트리밍, 푸시 알림 등)
- **securitySchemes**: 지원하는 보안 방식
- **skills**: 에이전트가 수행할 수 있는 작업 목록

## SDK 및 도구

A2A 프로토콜은 다양한 프로그래밍 언어를 위한 공식 SDK를 제공합니다:

### 공식 SDK

- **Python**:
  - Google SDK: `pip install a2a-python`
  - Python A2A: `pip install python-a2a`
- **JavaScript/TypeScript**: npm 패키지
- **Go**: Go 모듈
- **.NET**: `a2a-dotnet` NuGet 패키지
- **Java**: Maven/Gradle 아티팩트

### 커뮤니티 라이브러리

- **Python A2A** (`themanojdesai/python-a2a`): 풍부한 예제와 간편한 API 제공
- **A2A .NET SDK** (`a2aproject/a2a-dotnet`): .NET 생태계 완전 지원

## 시작하기

### 1. 스펙 검토
[a2a-protocol.org/latest/specification/](https://a2a-protocol.org/latest/specification/)에서 전체 사양 확인

### 2. SDK 설치
사용하는 언어에 맞는 SDK 설치

### 3. 샘플 탐색
a2a-samples 저장소에서 참조 구현 및 예제 확인

### 4. 에이전트 구현
프로토콜 표준을 따라 에이전트 구현

## 버전 관리 및 확장

### 버전 관리
- 프로토콜 버전은 `Major.Minor` 형식 사용
- 에이전트는 Agent Card에 지원하는 버전 선언
- 클라이언트는 `A2A-Version` 헤더를 통해 버전 요청 가능

### 확장성
- URI, 버전, 호환성 메타데이터로 확장 선언
- 코어 상호운용성을 깨지 않고 생태계 확장 가능
- 에이전트가 코어 스펙을 넘어 추가 기능 선언 가능

## 커뮤니티 및 기여

- **GitHub Issues**: 버그 보고 및 기능 요청
- **GitHub Discussions**: 커뮤니티 토론 및 질문
- **기여 가능**: Apache 2.0 라이선스 하에 오픈소스로 운영

## 사용 사례

A2A 프로토콜은 다음과 같은 시나리오에 적합합니다:

1. **엔터프라이즈 통합**: 여러 부서의 AI 에이전트가 협력하여 복잡한 업무 처리
2. **크로스 플랫폼 협업**: 서로 다른 벤더의 AI 에이전트 간 상호작용
3. **분산 AI 시스템**: 대규모 멀티 에이전트 시스템 구축
4. **자율 에이전트 네트워크**: 독립적으로 작동하면서도 필요시 협력하는 에이전트들

## 참고 자료

- [공식 웹사이트](https://a2a-protocol.org/latest/)
- [GitHub 저장소](https://github.com/a2aproject/A2A)
- [전체 스펙 문서](https://a2a-protocol.org/latest/specification/)
- [Google Developers Blog 발표](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
- [IBM A2A 가이드](https://www.ibm.com/think/topics/agent2agent-protocol)

## 다음 단계

- [A2A Architecture](./a2a-architecture.md) - 아키텍처 및 핵심 개념
- [A2A Implementation Guide](./a2a-implementation-guide.md) - 구현 가이드
- [A2A Examples](./a2a-examples.md) - 예제 및 사용 사례
