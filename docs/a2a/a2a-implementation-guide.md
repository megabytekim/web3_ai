# A2A Protocol Implementation Guide

## 시작하기

### 1. SDK 선택 및 설치

#### Python

**공식 SDK**:
```bash
# Google 공식 SDK
pip install a2a-python

# 또는 커뮤니티 Python A2A (권장 - 더 간편한 API)
pip install python-a2a
```

**기본 사용 예제 (python-a2a)**:
```python
from python_a2a import A2AClient, A2AServer, AgentCard, AgentSkill

# 클라이언트 생성
client = A2AClient("http://agent-server:5000")

# 간단한 요청
response = client.ask("What's the weather?")

# 서버 생성
class MyAgent(A2AServer):
    def __init__(self):
        agent_card = AgentCard(
            name="My A2A Agent",
            description="Custom agent description",
            url="http://localhost:5000"
        )
        super().__init__(agent_card=agent_card)

    def handle_task(self, task):
        # Task 처리 로직
        return task
```

#### JavaScript/TypeScript
```bash
npm install @a2a/sdk
```

```typescript
import { Agent, AgentCard, Task, Message } from '@a2a/sdk';

// 에이전트 초기화
const agent = new Agent({
  id: 'my-agent',
  name: 'My A2A Agent',
  endpoint: 'https://api.example.com/agent'
});
```

#### Go
```bash
go get github.com/a2aproject/a2a-go
```

```go
import "github.com/a2aproject/a2a-go"

// 에이전트 초기화
agent := a2a.NewAgent(&a2a.AgentConfig{
    ID:       "my-agent",
    Name:     "My A2A Agent",
    Endpoint: "https://api.example.com/agent",
})
```

### 2. 프로젝트 구조 설정

```
my-a2a-agent/
├── agent/
│   ├── __init__.py
│   ├── card.py          # Agent Card 정의
│   ├── handlers.py      # 메시지 핸들러
│   └── skills.py        # 스킬 구현
├── config/
│   ├── settings.py      # 설정
│   └── security.py      # 보안 설정
├── tests/
│   ├── test_agent.py
│   └── test_skills.py
├── main.py              # 엔트리 포인트
└── requirements.txt
```

## Agent Card 구현

### 기본 Agent Card

```python
# agent/card.py
from a2a import AgentCard, Capability, Skill, SecurityScheme

def create_agent_card():
    return AgentCard(
        id="document-analyzer",
        name="Document Analyzer",
        description="Analyzes and extracts information from documents",
        version="1.0.0",

        capabilities=Capability(
            streaming=True,
            multi_turn=True,
            file_upload=["application/pdf", "image/*"]
        ),

        skills=[
            Skill(
                name="extract-text",
                description="Extract text from PDF documents",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file": {
                            "type": "string",
                            "format": "uri"
                        }
                    },
                    "required": ["file"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "pages": {"type": "integer"}
                    }
                }
            )
        ],

        endpoints={
            "primary": "https://api.example.com/agent",
            "webhook": "https://api.example.com/webhooks"
        },

        security=SecurityScheme(
            schemes=["bearer", "oauth2"],
            auth_endpoint="https://auth.example.com/oauth2"
        )
    )
```

### Agent Card 서빙

```python
# main.py
from fastapi import FastAPI, Header, HTTPException
from agent.card import create_agent_card

app = FastAPI()

@app.get("/.well-known/agent-card")
async def get_agent_card(authorization: str = Header(None)):
    # 공개 버전 반환
    card = create_agent_card()

    # 인증된 클라이언트에게 확장 정보 제공
    if authorization and verify_token(authorization):
        card.extended = {
            "internal_capabilities": ["advanced-ocr", "handwriting"],
            "rate_limits": {
                "requests_per_minute": 100
            }
        }

    return card.to_dict()
```

## 메시지 처리 구현

### 메시지 핸들러

```python
# agent/handlers.py
from a2a import Message, Task, Part, TextPart, FilePart
from typing import AsyncGenerator

class MessageHandler:
    async def handle_message(self, message: Message, task: Task) -> Message:
        """동기식 메시지 처리"""
        # 메시지에서 파트 추출
        text_parts = [p for p in message.parts if isinstance(p, TextPart)]
        file_parts = [p for p in message.parts if isinstance(p, FilePart)]

        # 처리 로직
        response_text = await self.process_request(text_parts, file_parts)

        # 응답 메시지 생성
        return Message(
            role="agent",
            parts=[TextPart(text=response_text)]
        )

    async def handle_streaming_message(
        self,
        message: Message,
        task: Task
    ) -> AsyncGenerator[Message, None]:
        """스트리밍 메시지 처리"""
        # 진행 상황 업데이트 스트리밍
        yield Message(
            role="agent",
            parts=[TextPart(text="Processing your request...")]
        )

        # 중간 결과 스트리밍
        async for chunk in self.process_streaming(message):
            yield Message(
                role="agent",
                parts=[TextPart(text=chunk)]
            )

        # 최종 결과
        yield Message(
            role="agent",
            parts=[TextPart(text="Processing complete!")]
        )
```

### JSON-RPC 엔드포인트

```python
# main.py (continued)
from jsonrpcserver import method, Success, Error, dispatch
from agent.handlers import MessageHandler

handler = MessageHandler()

@method
async def SendMessage(message: dict, context_id: str = None) -> dict:
    """메시지 전송 처리"""
    try:
        # Message 객체 생성
        msg = Message.from_dict(message)

        # Task 생성
        task = Task.create(
            input_message=msg,
            context_id=context_id
        )

        # 메시지 처리
        response = await handler.handle_message(msg, task)

        # Task 완료
        task.complete(output_message=response)

        return Success(task.to_dict())

    except Exception as e:
        return Error(code=-32603, message=str(e))

@app.post("/rpc")
async def rpc_endpoint(request: Request):
    """JSON-RPC 엔드포인트"""
    body = await request.json()
    response = await dispatch(body)
    return response
```

## Context7 MCP 통합

Context7 MCP를 사용하면 A2A 에이전트가 실시간으로 최신 라이브러리 문서를 가져와 코드 생성 및 구현을 수행할 수 있습니다.

### Context7 MCP 설정

```python
# agent/context7.py
from typing import Dict, Any

class Context7Client:
    """Context7 MCP 클라이언트"""

    async def resolve_library_id(
        self,
        library_name: str,
        query: str
    ) -> Dict[str, Any]:
        """라이브러리 ID 해석"""
        # Context7 MCP resolve-library-id 도구 호출
        result = await mcp_client.call_tool(
            "resolve-library-id",
            {
                "libraryName": library_name,
                "query": query
            }
        )
        return result

    async def query_docs(
        self,
        library_id: str,
        query: str
    ) -> str:
        """문서 쿼리"""
        # Context7 MCP query-docs 도구 호출
        docs = await mcp_client.call_tool(
            "query-docs",
            {
                "libraryId": library_id,
                "query": query
            }
        )
        return docs
```

### 문서 기반 코드 생성 스킬

```python
# agent/skills.py
from agent.context7 import Context7Client

class DocumentationAwareSkills:
    def __init__(self):
        self.context7 = Context7Client()
        self.doc_cache = {}

    async def generate_code_with_docs(
        self,
        library: str,
        task_description: str
    ) -> str:
        """
        Context7를 사용하여 최신 문서를 가져온 후 코드 생성

        사용 예시:
        - library: "langchain", "a2a-sdk", "fastapi" 등
        - task_description: "Create a retrieval agent with vector store"
        """
        # 1. 라이브러리 ID 해석
        lib_info = await self.context7.resolve_library_id(
            library_name=library,
            query=task_description
        )

        library_id = lib_info['libraryId']

        # 2. 캐시 확인
        cache_key = f"{library_id}:{task_description}"
        if cache_key in self.doc_cache:
            docs = self.doc_cache[cache_key]
        else:
            # 3. 문서 쿼리
            docs = await self.context7.query_docs(
                library_id=library_id,
                query=task_description
            )
            self.doc_cache[cache_key] = docs

        # 4. LLM으로 코드 생성 (문서 기반)
        prompt = f"""
Based on the following documentation, generate code for: {task_description}

Documentation:
{docs}

Generate clean, production-ready code following best practices.
        """

        code = await self.llm.generate(prompt)
        return code
```

### A2A 메시지 핸들러에 Context7 통합

```python
# agent/handlers.py
from agent.skills import DocumentationAwareSkills
from a2a import Message, TextPart

class MessageHandler:
    def __init__(self):
        self.skills = DocumentationAwareSkills()

    async def handle_message(self, message: Message, task: Task) -> Message:
        """Context7를 활용한 메시지 처리"""
        # 메시지에서 요청 추출
        text = message.parts[0].text

        # "generate code using [library]" 패턴 감지
        if "generate code" in text.lower():
            # 라이브러리와 작업 추출
            library, task_desc = self.parse_code_request(text)

            # Context7로 문서 가져오고 코드 생성
            code = await self.skills.generate_code_with_docs(
                library=library,
                task_description=task_desc
            )

            return Message(
                role="agent",
                parts=[TextPart(text=f"```python\n{code}\n```")]
            )

        # 다른 메시지 처리
        return await self.default_handler(message, task)

    def parse_code_request(self, text: str) -> tuple[str, str]:
        """코드 요청 파싱"""
        # 예: "generate code using langchain for RAG agent"
        # -> ("langchain", "RAG agent")
        # 실제 구현은 더 정교해야 함
        import re
        match = re.search(r"using (\w+) for (.+)", text)
        if match:
            return match.group(1), match.group(2)
        return "python", text
```

### 실전 예제: A2A SDK 통합 생성

```python
# agent/a2a_generator.py
from agent.context7 import Context7Client

class A2AIntegrationGenerator:
    """A2A 프로토콜 통합 코드를 Context7 문서 기반으로 생성"""

    def __init__(self):
        self.context7 = Context7Client()

    async def generate_a2a_agent(
        self,
        language: str = "python"
    ) -> str:
        """
        A2A 에이전트 구현 코드 생성

        Context7를 사용하여 최신 A2A SDK 문서를 가져와서
        표준을 준수하는 에이전트 코드 생성
        """
        # 1. A2A SDK 문서 가져오기
        lib_info = await self.context7.resolve_library_id(
            library_name="a2a-sdk",
            query=f"Create {language} A2A agent with message handling"
        )

        # 2. 에이전트 구현 문서 쿼리
        agent_docs = await self.context7.query_docs(
            library_id=lib_info['libraryId'],
            query="Agent Card creation and message handler implementation"
        )

        # 3. 메시지 처리 문서 쿼리
        handler_docs = await self.context7.query_docs(
            library_id=lib_info['libraryId'],
            query="Synchronous and streaming message handlers"
        )

        # 4. 통합 코드 생성
        combined_docs = f"{agent_docs}\n\n{handler_docs}"

        code = await self.generate_code_from_docs(
            docs=combined_docs,
            language=language
        )

        return code

    async def generate_code_from_docs(
        self,
        docs: str,
        language: str
    ) -> str:
        """문서 기반 코드 생성"""
        prompt = f"""
Generate a complete A2A agent implementation in {language}.

Use the following official documentation:
{docs}

Requirements:
- Agent Card with capabilities
- Message handler (sync and streaming)
- Task management
- Error handling
- Type hints and documentation

Generate production-ready code.
        """

        return await self.llm.generate(prompt)
```

### Agent Card에 Context7 스킬 등록

```python
# agent/card.py
from a2a import AgentCard, Skill

def create_agent_card():
    return AgentCard(
        id="documentation-aware-agent",
        name="Documentation-Aware A2A Agent",
        description="A2A agent with real-time documentation fetching via Context7 MCP",

        skills=[
            Skill(
                name="generate-code-with-docs",
                description="Generate code using up-to-date library documentation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "library": {
                            "type": "string",
                            "description": "Library name (e.g., 'langchain', 'fastapi')"
                        },
                        "task": {
                            "type": "string",
                            "description": "Task description"
                        }
                    },
                    "required": ["library", "task"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "documentation_used": {"type": "string"}
                    }
                }
            ),
            Skill(
                name="generate-a2a-integration",
                description="Generate A2A protocol integration code",
                input_schema={
                    "type": "object",
                    "properties": {
                        "language": {
                            "type": "string",
                            "enum": ["python", "javascript", "go"]
                        }
                    },
                    "required": ["language"]
                }
            )
        ],

        endpoints={
            "primary": "https://api.example.com/agent"
        }
    )
```

### 사용 예시: Agent-to-Agent 협업

```python
# 에이전트 A: 코드 생성 요청
async def request_code_generation():
    """다른 A2A 에이전트에게 Context7 기반 코드 생성 요청"""
    message = Message(
        role="user",
        parts=[
            TextPart(
                text="Generate code using langchain for a RAG agent with ChromaDB"
            )
        ]
    )

    # Documentation-Aware Agent에게 메시지 전송
    task = await a2a_client.send_message(
        to_agent="documentation-aware-agent",
        message=message
    )

    # 응답 대기
    response = await task.wait_for_completion()
    generated_code = response.output_message.parts[0].text

    return generated_code

# 에이전트 B: Context7로 문서 가져와서 코드 생성
async def handle_code_generation_request(message: Message) -> Message:
    """Context7를 사용하여 코드 생성 요청 처리"""
    skills = DocumentationAwareSkills()

    code = await skills.generate_code_with_docs(
        library="langchain",
        task_description="RAG agent with ChromaDB"
    )

    return Message(
        role="agent",
        parts=[TextPart(text=f"```python\n{code}\n```")]
    )
```

### 베스트 프랙티스

1. **문서 캐싱**: 동일한 라이브러리/쿼리에 대해 문서 재사용
2. **호출 제한**: Context7 MCP 호출을 질문당 3회 이내로 제한
3. **구체적 쿼리**: 관련성 높은 문서를 위해 구체적인 쿼리 사용
4. **버전 명시**: 특정 버전 필요시 라이브러리 ID에 버전 포함
5. **에러 처리**: Context7 호출 실패 시 폴백 로직 구현

```python
# 에러 처리 예시
async def safe_generate_code(library: str, task: str) -> str:
    try:
        # Context7로 문서 가져오기 시도
        code = await skills.generate_code_with_docs(library, task)
        return code
    except Context7Error as e:
        # 폴백: 캐시된 문서 또는 기본 템플릿 사용
        logger.warning(f"Context7 failed: {e}, using fallback")
        return await generate_code_from_cache(library, task)
```

## Task 관리

### Task 저장소

```python
# agent/tasks.py
from typing import Dict, List, Optional
from a2a import Task, TaskState
import asyncio

class TaskRepository:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._lock = asyncio.Lock()

    async def create(self, task: Task) -> Task:
        """새 Task 생성"""
        async with self._lock:
            self._tasks[task.id] = task
            return task

    async def get(self, task_id: str) -> Optional[Task]:
        """Task 조회"""
        return self._tasks.get(task_id)

    async def update(self, task: Task) -> Task:
        """Task 업데이트"""
        async with self._lock:
            self._tasks[task.id] = task
            return task

    async def list(
        self,
        context_id: str = None,
        state: TaskState = None
    ) -> List[Task]:
        """Task 목록 조회"""
        tasks = list(self._tasks.values())

        if context_id:
            tasks = [t for t in tasks if t.context_id == context_id]

        if state:
            tasks = [t for t in tasks if t.state == state]

        return tasks

    async def delete(self, task_id: str) -> bool:
        """Task 삭제"""
        async with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False
```

### Task 라이프사이클 관리

```python
# agent/lifecycle.py
from a2a import Task, TaskState
from agent.tasks import TaskRepository

class TaskLifecycleManager:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    async def submit_task(self, task: Task) -> Task:
        """Task 제출"""
        task.state = TaskState.SUBMITTED
        return await self.repo.create(task)

    async def start_processing(self, task_id: str) -> Task:
        """Task 처리 시작"""
        task = await self.repo.get(task_id)
        if task:
            task.state = TaskState.WORKING
            return await self.repo.update(task)
        raise ValueError(f"Task {task_id} not found")

    async def request_input(self, task_id: str, prompt: str) -> Task:
        """추가 입력 요청"""
        task = await self.repo.get(task_id)
        if task:
            task.state = TaskState.INPUT_REQUIRED
            task.input_prompt = prompt
            return await self.repo.update(task)
        raise ValueError(f"Task {task_id} not found")

    async def complete_task(self, task_id: str, output) -> Task:
        """Task 완료"""
        task = await self.repo.get(task_id)
        if task:
            task.state = TaskState.COMPLETED
            task.output = output
            return await self.repo.update(task)
        raise ValueError(f"Task {task_id} not found")

    async def fail_task(self, task_id: str, error: str) -> Task:
        """Task 실패"""
        task = await self.repo.get(task_id)
        if task:
            task.state = TaskState.FAILED
            task.error = error
            return await self.repo.update(task)
        raise ValueError(f"Task {task_id} not found")

    async def cancel_task(self, task_id: str) -> Task:
        """Task 취소"""
        task = await self.repo.get(task_id)
        if task:
            if task.state not in [TaskState.COMPLETED, TaskState.FAILED]:
                task.state = TaskState.CANCELLED
                return await self.repo.update(task)
            raise ValueError("Cannot cancel completed or failed task")
        raise ValueError(f"Task {task_id} not found")
```

## 스트리밍 구현

### Server-Sent Events (SSE)

```python
# main.py (continued)
from fastapi.responses import StreamingResponse
from agent.handlers import MessageHandler

@app.post("/stream")
async def stream_endpoint(request: Request):
    """SSE 스트리밍 엔드포인트"""
    body = await request.json()
    message = Message.from_dict(body['message'])

    async def event_generator():
        task = Task.create(input_message=message)

        try:
            # 스트리밍 처리
            async for response_msg in handler.handle_streaming_message(message, task):
                # SSE 형식으로 전송
                data = response_msg.to_dict()
                yield f"data: {json.dumps(data)}\n\n"

            # 완료 이벤트
            task.complete()
            yield f"event: done\ndata: {json.dumps(task.to_dict())}\n\n"

        except Exception as e:
            # 오류 이벤트
            task.fail(str(e))
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 클라이언트 스트리밍 소비

```python
# client.py
import httpx
import json

async def consume_stream(url: str, message: dict):
    """SSE 스트림 소비"""
    async with httpx.AsyncClient() as client:
        async with client.stream('POST', url, json={'message': message}) as response:
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    print(f"Received: {data}")
                elif line.startswith('event: done'):
                    print("Stream complete")
                    break
                elif line.startswith('event: error'):
                    print(f"Error: {line}")
                    break
```

## Webhook 구현

### Webhook 전송

```python
# agent/webhooks.py
import httpx
import hmac
import hashlib
import time
from typing import Dict

class WebhookSender:
    def __init__(self, secret: str):
        self.secret = secret

    def generate_signature(self, payload: str) -> str:
        """HMAC-SHA256 서명 생성"""
        return hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    async def send(self, url: str, data: Dict) -> bool:
        """Webhook 전송"""
        payload = json.dumps(data)
        timestamp = str(int(time.time()))
        signature = self.generate_signature(f"{timestamp}.{payload}")

        headers = {
            'Content-Type': 'application/json',
            'X-A2A-Signature': signature,
            'X-A2A-Timestamp': timestamp
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    content=payload,
                    headers=headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Webhook send failed: {e}")
            return False
```

### Webhook 수신 및 검증

```python
# webhook_handler.py
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib
import time

app = FastAPI()

WEBHOOK_SECRET = "your-secret-key"

def verify_signature(payload: str, timestamp: str, signature: str) -> bool:
    """서명 검증"""
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        f"{timestamp}.{payload}".encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)

def verify_timestamp(timestamp: str, max_age: int = 300) -> bool:
    """타임스탬프 검증 (재생 공격 방지)"""
    try:
        ts = int(timestamp)
        current = int(time.time())
        return abs(current - ts) <= max_age
    except:
        return False

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Webhook 수신"""
    # 헤더 추출
    signature = request.headers.get('X-A2A-Signature')
    timestamp = request.headers.get('X-A2A-Timestamp')

    if not signature or not timestamp:
        raise HTTPException(status_code=401, detail="Missing signature headers")

    # 페이로드 읽기
    payload = await request.body()
    payload_str = payload.decode()

    # 타임스탬프 검증
    if not verify_timestamp(timestamp):
        raise HTTPException(status_code=401, detail="Invalid timestamp")

    # 서명 검증
    if not verify_signature(payload_str, timestamp, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 데이터 처리
    data = json.loads(payload_str)
    await process_webhook(data)

    return {"status": "ok"}
```

## 보안 구현

### 인증

```python
# config/security.py
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """JWT 토큰 검증"""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            "your-secret-key",
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 사용 예시
@app.post("/protected")
async def protected_endpoint(user: dict = Depends(verify_token)):
    return {"message": f"Hello {user['sub']}"}
```

### 권한 부여

```python
# agent/authorization.py
from typing import Optional

class AuthorizationService:
    def __init__(self):
        self.task_owners = {}  # task_id -> user_id

    def assign_owner(self, task_id: str, user_id: str):
        """Task 소유자 할당"""
        self.task_owners[task_id] = user_id

    def can_access_task(self, task_id: str, user_id: str) -> bool:
        """Task 접근 권한 확인"""
        owner = self.task_owners.get(task_id)
        return owner == user_id if owner else False

    def check_access(self, task_id: str, user_id: str):
        """접근 권한 체크 (예외 발생)"""
        if not self.can_access_task(task_id, user_id):
            raise HTTPException(
                status_code=404,  # 403이 아닌 404로 정보 유출 방지
                detail="Task not found"
            )
```

## 에러 처리

### 표준 에러 응답

```python
# agent/errors.py
from typing import Optional

class A2AError(Exception):
    def __init__(self, code: int, message: str, data: Optional[dict] = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

    def to_dict(self):
        error = {
            "code": self.code,
            "message": self.message
        }
        if self.data:
            error["data"] = self.data
        return {"error": error}

# 표준 에러 정의
class TaskNotFoundError(A2AError):
    def __init__(self, task_id: str):
        super().__init__(
            code=-32000,
            message="Task not found",
            data={"taskId": task_id}
        )

class UnauthorizedError(A2AError):
    def __init__(self):
        super().__init__(
            code=-32001,
            message="Unauthorized"
        )

class InvalidStateTransitionError(A2AError):
    def __init__(self, from_state: str, to_state: str):
        super().__init__(
            code=-32003,
            message="Invalid state transition",
            data={"from": from_state, "to": to_state}
        )
```

## 테스팅

### Unit Tests

```python
# tests/test_agent.py
import pytest
from agent.handlers import MessageHandler
from a2a import Message, TextPart, Task

@pytest.mark.asyncio
async def test_message_handling():
    handler = MessageHandler()

    # 테스트 메시지 생성
    message = Message(
        role="user",
        parts=[TextPart(text="Hello")]
    )

    task = Task.create(input_message=message)

    # 핸들러 호출
    response = await handler.handle_message(message, task)

    # 검증
    assert response.role == "agent"
    assert len(response.parts) > 0
```

### Integration Tests

```python
# tests/test_integration.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_send_message_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/rpc", json={
            "jsonrpc": "2.0",
            "method": "SendMessage",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": "Hello"}]
                }
            },
            "id": 1
        })

        assert response.status_code == 200
        data = response.json()
        assert "result" in data
```

## 배포

### Docker 컨테이너화

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes 배포

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: a2a-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: a2a-agent
  template:
    metadata:
      labels:
        app: a2a-agent
    spec:
      containers:
      - name: agent
        image: your-registry/a2a-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: A2A_SECRET
          valueFrom:
            secretKeyRef:
              name: a2a-secrets
              key: secret
```

## 모니터링 및 로깅

### 구조화된 로깅

```python
# agent/logging.py
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log(self, level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        self.logger.log(
            getattr(logging, level.upper()),
            json.dumps(log_entry)
        )
```

### 메트릭 수집

```python
# agent/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# 메트릭 정의
tasks_total = Counter('a2a_tasks_total', 'Total tasks', ['state'])
task_duration = Histogram('a2a_task_duration_seconds', 'Task duration')
active_tasks = Gauge('a2a_active_tasks', 'Active tasks')

# 사용 예시
def record_task_completion(task: Task):
    tasks_total.labels(state=task.state).inc()
    task_duration.observe(task.duration)
    active_tasks.dec()
```

## 다음 단계

- [A2A Protocol Overview](./a2a-protocol-overview.md) - 개요 및 소개
- [A2A Architecture](./a2a-architecture.md) - 아키텍처 및 핵심 개념
- [A2A Examples](./a2a-examples.md) - 예제 및 사용 사례
