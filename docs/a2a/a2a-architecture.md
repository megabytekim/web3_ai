# A2A Protocol Architecture

## 3계층 아키텍처

A2A 프로토콜은 명확하게 분리된 3계층 아키텍처를 사용합니다:

```
┌─────────────────────────────────────────┐
│   Protocol Bindings (구체적 구현)        │
│   - JSON-RPC over HTTP/HTTPS            │
│   - gRPC                                │
│   - HTTP/REST                           │
├─────────────────────────────────────────┤
│   Abstract Operations (추상 연산)        │
│   - Send Message                        │
│   - Get Task / List Tasks               │
│   - Cancel Task                         │
│   - Subscribe to Task                   │
├─────────────────────────────────────────┤
│   Canonical Data Model (정규 데이터)     │
│   - Tasks, Messages, Agent Cards        │
│   - Protocol Buffer 정의                │
└─────────────────────────────────────────┘
```

### 1. Canonical Data Model (정규 데이터 모델)
Protocol Buffer 정의를 통한 핵심 구조:
- **Tasks**: 작업 단위
- **Messages**: 통신 턴
- **Agent Cards**: 에이전트 메타데이터

### 2. Abstract Operations (추상 연산)
바인딩에 독립적인 기능:
- Send Message: 메시지 전송
- Get Task: 작업 상태 조회
- List Tasks: 작업 목록 조회
- Cancel Task: 작업 취소
- Subscribe to Task: 작업 업데이트 구독

### 3. Protocol Bindings (프로토콜 바인딩)
구체적 구현:
- JSON-RPC 2.0
- gRPC
- HTTP/REST

## 핵심 개념

### Tasks (작업)

Tasks는 A2A 프로토콜의 기본 작업 단위입니다.

#### Task 구조
```json
{
  "id": "task-123",
  "contextId": "conv-456",
  "state": "working",
  "createdAt": "2025-01-01T00:00:00Z",
  "updatedAt": "2025-01-01T00:05:00Z",
  "input": { /* Message */ },
  "output": { /* Message or Artifact */ }
}
```

#### Task 라이프사이클

```
        submitted
            │
            ▼
         working ──────────> input-required
            │                      │
            │◄─────────────────────┘
            │
    ┌───────┼───────┬─────────┐
    ▼       ▼       ▼         ▼
completed failed cancelled rejected
```

**상태 설명**:
- `submitted`: 작업이 제출되고 처리 대기 중
- `working`: 에이전트가 작업 처리 중
- `input-required`: 클라이언트의 추가 입력 필요
- `completed`: 작업 성공적으로 완료
- `failed`: 작업 처리 중 오류 발생
- `cancelled`: 클라이언트 요청으로 작업 취소
- `rejected`: 에이전트가 작업 거부

#### Context ID
`contextId`는 관련된 작업/메시지를 대화로 그룹화합니다:
- 클라이언트는 `taskId` 또는 `contextId`를 통해 작업 참조 가능
- 에이전트는 작업 참조에서 컨텍스트 추론
- 불일치하는 context/task ID 쌍은 거부됨

#### Python SDK로 Task 관리하기

```python
from python_a2a import A2AServer, TaskStatus, TaskState

class MyAgent(A2AServer):
    def handle_task(self, task):
        """Task 처리 핸들러"""
        # Task 정보 추출
        message_data = task.message or {}
        content = message_data.get("content", {})
        text = content.get("text", "")

        # 작업 처리
        try:
            result = self.process_request(text)

            # 성공 시 completed 상태로 반환
            task.artifacts = [
                {
                    "parts": [
                        {"type": "text", "text": result}
                    ]
                }
            ]
            task.status = TaskStatus(state=TaskState.COMPLETED)

        except ValueError as e:
            # 입력 필요 시 input-required 상태
            task.status = TaskStatus(
                state=TaskState.INPUT_REQUIRED,
                message="Please provide more information"
            )

        except Exception as e:
            # 실패 시 failed 상태
            task.status = TaskStatus(
                state=TaskState.FAILED,
                message=str(e)
            )

        return task
```

### Messages (메시지)

Messages는 에이전트 간 통신 턴을 나타냅니다.

#### Message 구조
```json
{
  "role": "user",  // or "agent"
  "parts": [
    {
      "type": "text",
      "text": "Hello, can you help me?"
    }
  ],
  "metadata": {
    "timestamp": "2025-01-01T00:00:00Z"
  }
}
```

#### Part Types (파트 유형)

**1. TextPart (텍스트)**
```json
{
  "type": "text",
  "text": "This is a text message"
}
```

**2. FilePart (파일 참조)**
```json
{
  "type": "file",
  "name": "document.pdf",
  "mimeType": "application/pdf",
  "uri": "https://storage.example.com/file123",
  "size": 1024000
}
```

**3. DataPart (구조화된 데이터)**
```json
{
  "type": "data",
  "mimeType": "application/json",
  "data": {
    "key": "value",
    "nested": {
      "field": 123
    }
  }
}
```

#### Python SDK로 Message 전송하기

```python
from python_a2a import A2AClient, Message, TextContent, MessageRole

# 클라이언트 초기화
client = A2AClient("http://agent-server:5000")

# 1. 간단한 텍스트 메시지
response = client.ask("What's the weather in Seoul?")
print(f"Response: {response}")

# 2. Message 객체 사용 (더 많은 제어)
message = Message(
    content=TextContent(text="Analyze this data"),
    role=MessageRole.USER
)
response_msg = client.send_message(message)
print(f"Agent reply: {response_msg.content.text}")

# 3. 대화 컨텍스트 유지 (contextId 사용)
context_id = "conversation-123"
msg1 = client.send_message(
    Message(
        content=TextContent(text="Hello, I need help"),
        role=MessageRole.USER
    ),
    context_id=context_id
)

# 같은 컨텍스트로 후속 메시지
msg2 = client.send_message(
    Message(
        content=TextContent(text="Can you elaborate?"),
        role=MessageRole.USER
    ),
    context_id=context_id
)
```

### Agent Cards (에이전트 카드)

Agent Card는 에이전트의 능력과 속성을 설명하는 JSON 메타데이터 문서입니다.

#### Agent Card 구조
```json
{
  "id": "agent-123",
  "name": "Document Analyzer",
  "description": "Analyzes and extracts information from documents",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "multiTurn": true,
    "fileUpload": ["application/pdf", "image/*"]
  },
  "skills": [
    {
      "name": "extract-text",
      "description": "Extract text from PDF documents",
      "inputSchema": { /* JSON Schema */ },
      "outputSchema": { /* JSON Schema */ }
    }
  ],
  "endpoints": {
    "primary": "https://api.example.com/agent",
    "webhook": "https://api.example.com/webhooks"
  },
  "security": {
    "schemes": ["bearer", "oauth2"],
    "authEndpoint": "https://auth.example.com/oauth2"
  }
}
```

#### Extended Agent Cards
민감한 정보를 위해 인증된 클라이언트에게만 제공되는 확장 카드:
- 내부 능력 상세 정보
- 제한된 기능 접근
- 추가 보안 요구사항

#### Python SDK로 Agent Card 정의하기

```python
from python_a2a import AgentCard, AgentSkill

# Agent Card 생성
agent_card = AgentCard(
    name="Weather Information Agent",
    description="Provides weather forecasts and current conditions",
    url="http://localhost:5000",
    version="1.0.0",
    skills=[
        AgentSkill(
            name="Current Weather",
            description="Get current weather conditions for a location",
            tags=["weather", "current", "conditions"],
            examples=[
                "What's the weather in Seoul?",
                "Current temperature in Tokyo"
            ]
        ),
        AgentSkill(
            name="Weather Forecast",
            description="Get weather forecast for upcoming days",
            tags=["weather", "forecast", "prediction"],
            examples=[
                "7-day forecast for New York",
                "Will it rain tomorrow in London?"
            ]
        )
    ]
)

# Agent Card 정보 확인
print(f"Agent: {agent_card.name}")
print(f"Skills: {[skill.name for skill in agent_card.skills]}")
```

## 통신 패턴

### 1. 동기식 요청-응답

```
Client                    Remote Agent
  │                            │
  ├─── Send Message ──────────>│
  │                            │
  │<─── Task/Message ──────────┤
  │                            │
```

### 2. 스트리밍 (Server-Sent Events)

```
Client                    Remote Agent
  │                            │
  ├─── Send Streaming Msg ────>│
  │                            │
  │<─── SSE: update 1 ─────────┤
  │<─── SSE: update 2 ─────────┤
  │<─── SSE: update 3 ─────────┤
  │<─── SSE: completed ────────┤
  │                            │
```

### 3. 비동기 Push (Webhooks)

```
Client                    Remote Agent
  │                            │
  ├─── Send Message ──────────>│
  │<─── Task (working) ────────┤
  │                            │
  │                            │ (processing...)
  │                            │
  │<─── Webhook: update ───────┤
  │<─── Webhook: completed ────┤
  │                            │
```

## 업데이트 전달 메커니즘

클라이언트는 3가지 방법으로 작업 업데이트를 받을 수 있습니다:

### 1. Polling (폴링)
- **방식**: 주기적인 Get Task 호출
- **장점**: 구현 간단
- **단점**: 높은 지연시간, 불필요한 요청
- **적합**: 실시간성이 중요하지 않은 경우

```
while task.state not in terminal_states:
    task = get_task(task_id)
    time.sleep(poll_interval)
```

### 2. Streaming (스트리밍)
- **방식**: 지속적 연결을 통한 실시간 이벤트 (SSE)
- **장점**: 낮은 지연시간, 실시간 업데이트
- **단점**: 연결 유지 필요
- **적합**: 실시간 모니터링이 필요한 경우

```
stream = subscribe_to_task(task_id)
for update in stream:
    handle_update(update)
```

### 3. Push Notifications (푸시 알림)
- **방식**: Webhook HTTP POST를 통한 비동기 전달
- **장점**: 연결 유지 불필요, 효율적
- **단점**: Webhook 엔드포인트 설정 필요
- **적합**: 서버 측 통합

```
@app.route('/webhook', methods=['POST'])
def webhook_handler():
    update = request.json
    handle_update(update)
```

## 보안 아키텍처

### 인증 (Authentication)

지원되는 인증 방식:
- **HTTP Authentication**: Basic, Bearer Token
- **OAuth 2.0**: 표준 OAuth2 플로우
- **API Keys**: 헤더 또는 쿼리 파라미터
- **mTLS**: 상호 TLS 인증

### 권한 부여 (Authorization)

```
┌──────────────┐
│   Client     │
│  (Task 123)  │
└──────┬───────┘
       │ Request Task 123
       ▼
┌──────────────┐    Check:
│   Server     │    - Is client authenticated?
│              │    - Does client own Task 123?
│              │    - Is task in correct context?
└──────────────┘
```

**핵심 원칙**:
1. 데이터 접근은 인증된 클라이언트로만 제한
2. 클라이언트는 자신이 권한을 가진 작업만 접근
3. "찾을 수 없음"과 "권한 없음"을 구분하지 않음 (정보 유출 방지)

### Webhook 보안

Webhook 엔드포인트 검증:
```
1. HTTPS 필수
2. 서명 검증 (HMAC-SHA256)
3. Timestamp 확인 (재생 공격 방지)
4. IP 화이트리스트 (선택사항)
```

## 멀티턴 상호작용

### Context 관리

```
Conversation (contextId: "conv-123")
  │
  ├─ Task 1: "What's the weather?"
  │    └─ Response: "It's sunny, 75°F"
  │
  ├─ Task 2: "How about tomorrow?"
  │    └─ Response: "Partly cloudy, 72°F"
  │    └─ (references contextId: "conv-123")
  │
  └─ Task 3: "Should I bring an umbrella?"
       └─ Response: "No, low chance of rain"
       └─ (references contextId: "conv-123")
```

### 컨텍스트 연속성

에이전트는 다음을 통해 컨텍스트 유지:
1. `contextId`를 통한 대화 그룹화
2. 이전 작업 참조를 통한 이력 추론
3. 공유 메모리 및 상태 관리
4. 불일치 감지 및 거부

## 확장성 및 확장

### Extension 선언

```json
{
  "extensions": [
    {
      "uri": "https://example.com/extensions/custom-feature",
      "version": "1.0",
      "compatibility": "optional",
      "metadata": {
        "description": "Custom feature extension",
        "params": { /* schema */ }
      }
    }
  ]
}
```

### 버전 협상

```
Client                    Server
  │                          │
  ├─ A2A-Version: 1.1 ──────>│
  │                          │
  │                          │ Supports: 1.0, 1.1, 1.2
  │                          │ Use: 1.1
  │                          │
  │<─ A2A-Version: 1.1 ──────┤
  │                          │
```

## 오류 처리

### 표준 오류 코드

```json
{
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {
      "taskId": "task-123",
      "details": "Processing failed due to timeout"
    }
  }
}
```

**JSON-RPC 오류 코드**:
- `-32700`: Parse error (구문 오류)
- `-32600`: Invalid request (잘못된 요청)
- `-32601`: Method not found (메서드 없음)
- `-32602`: Invalid params (잘못된 파라미터)
- `-32603`: Internal error (내부 오류)

**A2A 커스텀 오류 코드**:
- `-32000`: Task not found
- `-32001`: Unauthorized
- `-32002`: Task already cancelled
- `-32003`: Invalid state transition

## 관찰성 (Observability)

### 분산 추적

```
Client Request
  │
  ├─ Trace ID: abc123
  │  Span ID: span1
  │
  ▼
Remote Agent 1
  │
  ├─ Trace ID: abc123
  │  Span ID: span2
  │  Parent: span1
  │
  ▼
Remote Agent 2
  │
  ├─ Trace ID: abc123
  │  Span ID: span3
  │  Parent: span2
```

### 로깅 및 모니터링

권장 메트릭:
- 작업 성공/실패율
- 평균 작업 처리 시간
- 동시 작업 수
- 메시지 처리량
- 오류율 및 유형

## 다음 단계

- [A2A Protocol Overview](./a2a-protocol-overview.md) - 개요 및 소개
- [A2A Implementation Guide](./a2a-implementation-guide.md) - 구현 가이드
- [A2A Examples](./a2a-examples.md) - 예제 및 사용 사례
