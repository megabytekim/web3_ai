# A2A Protocol Examples

## 예제 1: 간단한 텍스트 대화

### 시나리오
사용자가 날씨 정보 에이전트에게 현재 날씨를 물어봅니다.

### 클라이언트 코드

```python
import httpx
import json

async def ask_weather(location: str):
    # Agent Card 조회
    async with httpx.AsyncClient() as client:
        card_response = await client.get(
            "https://weather-agent.example.com/.well-known/agent-card"
        )
        agent_card = card_response.json()
        print(f"Connected to: {agent_card['name']}")

        # 메시지 전송
        rpc_request = {
            "jsonrpc": "2.0",
            "method": "SendMessage",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "type": "text",
                            "text": f"What's the weather in {location}?"
                        }
                    ]
                }
            },
            "id": 1
        }

        response = await client.post(
            agent_card['endpoints']['primary'] + "/rpc",
            json=rpc_request
        )

        result = response.json()
        task = result['result']

        print(f"Response: {task['output']['parts'][0]['text']}")
        return task

# 사용
await ask_weather("Seoul")
```

### 서버 응답

```json
{
  "jsonrpc": "2.0",
  "result": {
    "id": "task-123",
    "state": "completed",
    "input": {
      "role": "user",
      "parts": [{"type": "text", "text": "What's the weather in Seoul?"}]
    },
    "output": {
      "role": "agent",
      "parts": [
        {
          "type": "text",
          "text": "The current weather in Seoul is sunny with a temperature of 22°C (72°F). Wind speed is 10 km/h from the west."
        }
      ]
    }
  },
  "id": 1
}
```

## 예제 2: 파일 처리

### 시나리오
사용자가 PDF 문서를 분석 에이전트에게 전송하여 텍스트를 추출합니다.

### 클라이언트 코드

```python
async def analyze_document(file_path: str):
    # 파일 업로드 (S3, GCS 등)
    file_url = await upload_to_storage(file_path)

    async with httpx.AsyncClient() as client:
        rpc_request = {
            "jsonrpc": "2.0",
            "method": "SendMessage",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "type": "text",
                            "text": "Please extract text from this document"
                        },
                        {
                            "type": "file",
                            "name": "document.pdf",
                            "mimeType": "application/pdf",
                            "uri": file_url,
                            "size": 1024000
                        }
                    ]
                }
            },
            "id": 1
        }

        response = await client.post(
            "https://doc-analyzer.example.com/rpc",
            json=rpc_request,
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )

        result = response.json()
        task = result['result']

        # 결과 처리
        for part in task['output']['parts']:
            if part['type'] == 'text':
                print(f"Extracted text: {part['text']}")
            elif part['type'] == 'data':
                print(f"Metadata: {part['data']}")

# 사용
await analyze_document("report.pdf")
```

### 서버 응답

```json
{
  "jsonrpc": "2.0",
  "result": {
    "id": "task-456",
    "state": "completed",
    "output": {
      "role": "agent",
      "parts": [
        {
          "type": "text",
          "text": "Document Analysis Report\n\nTotal Pages: 15\nWord Count: 3,245\n\nSummary: This document contains..."
        },
        {
          "type": "data",
          "mimeType": "application/json",
          "data": {
            "pages": 15,
            "words": 3245,
            "language": "en",
            "confidence": 0.98
          }
        }
      ]
    }
  },
  "id": 1
}
```

## 예제 3: 스트리밍 응답

### 시나리오
사용자가 대용량 데이터를 처리하는 동안 실시간으로 진행 상황을 받아봅니다.

### 클라이언트 코드

```python
async def process_with_streaming(data: str):
    async with httpx.AsyncClient() as client:
        request_data = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": data}]
            }
        }

        async with client.stream(
            'POST',
            "https://processor.example.com/stream",
            json=request_data,
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    data = json.loads(line[6:])

                    # 메시지 업데이트 처리
                    if 'parts' in data:
                        for part in data['parts']:
                            if part['type'] == 'text':
                                print(f"Update: {part['text']}")

                elif line.startswith('event: done'):
                    print("Processing complete!")
                    data = json.loads(line.split('data: ')[1])
                    return data

# 사용
result = await process_with_streaming("Process this large dataset...")
```

### 서버 SSE 스트림

```
data: {"role": "agent", "parts": [{"type": "text", "text": "Starting analysis..."}]}

data: {"role": "agent", "parts": [{"type": "text", "text": "Processing chunk 1 of 10..."}]}

data: {"role": "agent", "parts": [{"type": "text", "text": "Processing chunk 2 of 10..."}]}

...

event: done
data: {"id": "task-789", "state": "completed", "output": {...}}
```

## 예제 4: 멀티턴 대화

### 시나리오
사용자가 여행 계획 에이전트와 여러 차례 대화하며 여행 일정을 작성합니다.

### 클라이언트 코드

```python
class ConversationClient:
    def __init__(self, agent_url: str):
        self.agent_url = agent_url
        self.context_id = None
        self.client = httpx.AsyncClient()

    async def send_message(self, text: str) -> dict:
        rpc_request = {
            "jsonrpc": "2.0",
            "method": "SendMessage",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": text}]
                },
                "contextId": self.context_id
            },
            "id": 1
        }

        response = await self.client.post(
            f"{self.agent_url}/rpc",
            json=rpc_request
        )

        result = response.json()
        task = result['result']

        # 첫 메시지면 contextId 저장
        if not self.context_id and task.get('contextId'):
            self.context_id = task['contextId']

        return task

# 사용 예시
conversation = ConversationClient("https://travel-agent.example.com")

# 1. 초기 요청
task1 = await conversation.send_message(
    "I want to plan a trip to Japan"
)
print(task1['output']['parts'][0]['text'])
# "Great! When are you planning to visit Japan?"

# 2. 후속 응답 (같은 컨텍스트)
task2 = await conversation.send_message(
    "In April, for about 5 days"
)
print(task2['output']['parts'][0]['text'])
# "April is cherry blossom season! What cities would you like to visit?"

# 3. 추가 정보 제공
task3 = await conversation.send_message(
    "Tokyo and Kyoto"
)
print(task3['output']['parts'][0]['text'])
# "Perfect! Here's a suggested 5-day itinerary for Tokyo and Kyoto..."
```

## 예제 5: 에이전트 간 협업

### 시나리오
문서 분석 에이전트가 번역 에이전트를 호출하여 협업합니다.

### Document Analyzer Agent

```python
class DocumentAnalyzer:
    def __init__(self):
        self.translator_url = "https://translator-agent.example.com"

    async def analyze_document(self, file_url: str, target_lang: str):
        # 1. 텍스트 추출
        text = await self.extract_text(file_url)

        # 2. 언어 감지
        detected_lang = await self.detect_language(text)

        # 3. 번역이 필요한 경우 번역 에이전트 호출
        if detected_lang != target_lang:
            translated_text = await self.call_translator(
                text,
                source_lang=detected_lang,
                target_lang=target_lang
            )
        else:
            translated_text = text

        return {
            "original_language": detected_lang,
            "text": translated_text
        }

    async def call_translator(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """번역 에이전트에게 A2A 호출"""
        async with httpx.AsyncClient() as client:
            rpc_request = {
                "jsonrpc": "2.0",
                "method": "SendMessage",
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [
                            {
                                "type": "text",
                                "text": f"Translate from {source_lang} to {target_lang}: {text}"
                            }
                        ]
                    }
                },
                "id": 1
            }

            response = await client.post(
                f"{self.translator_url}/rpc",
                json=rpc_request,
                headers={"Authorization": f"Bearer {AGENT_TOKEN}"}
            )

            result = response.json()
            return result['result']['output']['parts'][0]['text']
```

## 예제 6: Task 상태 폴링

### 시나리오
장시간 실행되는 작업의 상태를 주기적으로 확인합니다.

### 클라이언트 코드

```python
import asyncio

async def submit_and_wait(message: dict):
    async with httpx.AsyncClient() as client:
        # 1. Task 제출
        submit_response = await client.post(
            "https://processor.example.com/rpc",
            json={
                "jsonrpc": "2.0",
                "method": "SendMessage",
                "params": {"message": message},
                "id": 1
            }
        )

        task = submit_response.json()['result']
        task_id = task['id']

        # 2. Task 완료까지 폴링
        while task['state'] not in ['completed', 'failed', 'cancelled']:
            await asyncio.sleep(2)  # 2초 대기

            # Task 상태 조회
            status_response = await client.post(
                "https://processor.example.com/rpc",
                json={
                    "jsonrpc": "2.0",
                    "method": "GetTask",
                    "params": {"taskId": task_id},
                    "id": 2
                }
            )

            task = status_response.json()['result']
            print(f"Status: {task['state']}")

        # 3. 최종 결과
        if task['state'] == 'completed':
            print(f"Result: {task['output']}")
        elif task['state'] == 'failed':
            print(f"Error: {task['error']}")

        return task
```

## 예제 7: Webhook을 통한 비동기 알림

### 시나리오
작업 완료 시 Webhook을 통해 클라이언트에게 알림을 보냅니다.

### 클라이언트 Webhook 서버

```python
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib

app = FastAPI()

WEBHOOK_SECRET = "your-webhook-secret"

def verify_webhook(payload: str, timestamp: str, signature: str) -> bool:
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        f"{timestamp}.{payload}".encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@app.post("/webhook/a2a")
async def receive_webhook(request: Request):
    # 헤더 검증
    signature = request.headers.get('X-A2A-Signature')
    timestamp = request.headers.get('X-A2A-Timestamp')

    payload = await request.body()
    payload_str = payload.decode()

    if not verify_webhook(payload_str, timestamp, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 데이터 처리
    data = json.loads(payload_str)

    if data['type'] == 'task.completed':
        task = data['task']
        print(f"Task {task['id']} completed!")
        print(f"Result: {task['output']}")
        # 결과 처리 로직...

    elif data['type'] == 'task.failed':
        task = data['task']
        print(f"Task {task['id']} failed: {task['error']}")
        # 오류 처리 로직...

    return {"status": "received"}

# Task 제출 시 webhook URL 지정
async def submit_with_webhook():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://processor.example.com/rpc",
            json={
                "jsonrpc": "2.0",
                "method": "SendMessage",
                "params": {
                    "message": {...},
                    "webhookUrl": "https://my-app.example.com/webhook/a2a"
                },
                "id": 1
            }
        )
        return response.json()
```

## 예제 8: 능력 발견 및 동적 라우팅

### 시나리오
여러 에이전트 중에서 요청에 가장 적합한 에이전트를 선택합니다.

### 라우터 구현

```python
class AgentRouter:
    def __init__(self):
        self.agents = {}  # agent_id -> agent_card

    async def discover_agent(self, agent_url: str):
        """에이전트 발견 및 등록"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{agent_url}/.well-known/agent-card"
            )
            card = response.json()
            self.agents[card['id']] = {
                'card': card,
                'url': agent_url
            }
            return card

    def find_capable_agent(self, required_skill: str):
        """특정 스킬을 가진 에이전트 찾기"""
        for agent_id, agent_info in self.agents.items():
            card = agent_info['card']
            for skill in card.get('skills', []):
                if skill['name'] == required_skill:
                    return agent_info

        return None

    async def route_request(self, skill: str, message: dict):
        """요청을 적절한 에이전트로 라우팅"""
        agent_info = self.find_capable_agent(skill)

        if not agent_info:
            raise ValueError(f"No agent found with skill: {skill}")

        # 선택된 에이전트에게 요청 전송
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{agent_info['url']}/rpc",
                json={
                    "jsonrpc": "2.0",
                    "method": "SendMessage",
                    "params": {"message": message},
                    "id": 1
                }
            )
            return response.json()

# 사용 예시
router = AgentRouter()

# 에이전트 발견
await router.discover_agent("https://translator.example.com")
await router.discover_agent("https://summarizer.example.com")
await router.discover_agent("https://analyzer.example.com")

# 동적 라우팅
result = await router.route_request(
    skill="translate",
    message={
        "role": "user",
        "parts": [{"type": "text", "text": "Translate this to Korean"}]
    }
)
```

## 예제 9: 오류 처리 및 재시도

### 클라이언트 코드

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class ResilientA2AClient:
    def __init__(self, agent_url: str):
        self.agent_url = agent_url

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def send_message_with_retry(self, message: dict):
        """재시도 로직이 있는 메시지 전송"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.agent_url}/rpc",
                    json={
                        "jsonrpc": "2.0",
                        "method": "SendMessage",
                        "params": {"message": message},
                        "id": 1
                    }
                )

                result = response.json()

                # JSON-RPC 오류 확인
                if 'error' in result:
                    error = result['error']
                    if error['code'] == -32603:  # Internal error
                        # 재시도 가능한 오류
                        raise Exception(f"Retriable error: {error['message']}")
                    else:
                        # 재시도 불가능한 오류
                        raise ValueError(f"Permanent error: {error['message']}")

                return result['result']

        except httpx.TimeoutException:
            print("Request timeout, retrying...")
            raise
        except httpx.NetworkError:
            print("Network error, retrying...")
            raise

# 사용
client = ResilientA2AClient("https://agent.example.com")
try:
    task = await client.send_message_with_retry(message)
    print(f"Success: {task}")
except Exception as e:
    print(f"Failed after retries: {e}")
```

## 예제 10: 복잡한 워크플로우

### 시나리오
문서 분석 → 요약 → 번역 → 이메일 발송의 복잡한 워크플로우

### 워크플로우 오케스트레이터

```python
class DocumentProcessingWorkflow:
    def __init__(self):
        self.analyzer_url = "https://analyzer.example.com"
        self.summarizer_url = "https://summarizer.example.com"
        self.translator_url = "https://translator.example.com"
        self.emailer_url = "https://emailer.example.com"

    async def process_document(
        self,
        file_url: str,
        target_lang: str,
        recipient_email: str
    ):
        context_id = f"workflow-{uuid.uuid4()}"

        try:
            # 1. 문서 분석
            print("Step 1: Analyzing document...")
            analysis = await self.call_agent(
                self.analyzer_url,
                {"type": "file", "uri": file_url},
                context_id
            )

            # 2. 요약 생성
            print("Step 2: Generating summary...")
            summary = await self.call_agent(
                self.summarizer_url,
                {"type": "text", "text": analysis['text']},
                context_id
            )

            # 3. 번역
            print("Step 3: Translating...")
            translation = await self.call_agent(
                self.translator_url,
                {
                    "type": "text",
                    "text": f"Translate to {target_lang}: {summary['text']}"
                },
                context_id
            )

            # 4. 이메일 발송
            print("Step 4: Sending email...")
            email_result = await self.call_agent(
                self.emailer_url,
                {
                    "type": "data",
                    "data": {
                        "to": recipient_email,
                        "subject": "Document Summary",
                        "body": translation['text']
                    }
                },
                context_id
            )

            return {
                "status": "completed",
                "context_id": context_id,
                "steps": {
                    "analysis": analysis,
                    "summary": summary,
                    "translation": translation,
                    "email": email_result
                }
            }

        except Exception as e:
            print(f"Workflow failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "context_id": context_id
            }

    async def call_agent(self, agent_url: str, part: dict, context_id: str):
        """에이전트 호출 헬퍼"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{agent_url}/rpc",
                json={
                    "jsonrpc": "2.0",
                    "method": "SendMessage",
                    "params": {
                        "message": {
                            "role": "user",
                            "parts": [part]
                        },
                        "contextId": context_id
                    },
                    "id": 1
                }
            )

            result = response.json()
            return result['result']['output']['parts'][0]

# 사용
workflow = DocumentProcessingWorkflow()
result = await workflow.process_document(
    file_url="https://storage.example.com/doc.pdf",
    target_lang="ko",
    recipient_email="user@example.com"
)
```

## 예제 11: Context7 MCP를 활용한 문서 기반 코드 생성

### 시나리오
개발자가 A2A 에이전트에게 특정 라이브러리를 사용한 코드 생성을 요청합니다. 에이전트는 Context7 MCP를 통해 최신 문서를 가져와 정확한 코드를 생성합니다.

### Context7 MCP 클라이언트 설정

```python
# context7_client.py
from typing import Dict, Any
import httpx

class Context7MCPClient:
    """Context7 MCP 클라이언트"""

    def __init__(self, mcp_endpoint: str):
        self.mcp_endpoint = mcp_endpoint
        self.cache = {}

    async def resolve_library_id(
        self,
        library_name: str,
        query: str
    ) -> str:
        """라이브러리 ID 해석"""
        cache_key = f"resolve:{library_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.mcp_endpoint}/resolve-library-id",
                json={
                    "libraryName": library_name,
                    "query": query
                }
            )

            result = response.json()
            library_id = result['libraryId']
            self.cache[cache_key] = library_id

            return library_id

    async def query_docs(
        self,
        library_id: str,
        query: str
    ) -> str:
        """문서 쿼리"""
        cache_key = f"docs:{library_id}:{query}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.mcp_endpoint}/query-docs",
                json={
                    "libraryId": library_id,
                    "query": query
                }
            )

            docs = response.json()['documentation']
            self.cache[cache_key] = docs

            return docs
```

### 코드 생성 에이전트 구현

```python
# code_generation_agent.py
from a2a import Agent, Message, Task, TextPart
from context7_client import Context7MCPClient
import openai

class CodeGenerationAgent:
    """Context7 MCP를 활용한 코드 생성 A2A 에이전트"""

    def __init__(self, agent_id: str, context7_endpoint: str):
        self.agent_id = agent_id
        self.context7 = Context7MCPClient(context7_endpoint)
        self.openai_client = openai.AsyncOpenAI()

    async def handle_message(
        self,
        message: Message,
        task: Task
    ) -> Message:
        """메시지 처리: 코드 생성 요청"""
        # 요청 파싱
        text = message.parts[0].text
        library, task_desc = self.parse_request(text)

        # 1. Context7로 라이브러리 ID 해석
        library_id = await self.context7.resolve_library_id(
            library_name=library,
            query=task_desc
        )

        print(f"Resolved library: {library} -> {library_id}")

        # 2. 관련 문서 가져오기
        docs = await self.context7.query_docs(
            library_id=library_id,
            query=task_desc
        )

        print(f"Fetched documentation ({len(docs)} chars)")

        # 3. 문서 기반 코드 생성
        code = await self.generate_code(
            library=library,
            task_description=task_desc,
            documentation=docs
        )

        # 4. 응답 반환
        return Message(
            role="agent",
            parts=[
                TextPart(
                    text=f"```python\n{code}\n```\n\n"
                         f"Generated using {library} documentation from Context7 MCP."
                )
            ]
        )

    def parse_request(self, text: str) -> tuple[str, str]:
        """요청 텍스트 파싱"""
        # 예: "Generate code using langchain for RAG agent"
        import re
        match = re.search(
            r"(?:generate|create|write|build).*(?:using|with)\s+(\w+)\s+for\s+(.+)",
            text,
            re.IGNORECASE
        )
        if match:
            return match.group(1), match.group(2)

        # 기본값
        return "python", text

    async def generate_code(
        self,
        library: str,
        task_description: str,
        documentation: str
    ) -> str:
        """LLM으로 코드 생성"""
        prompt = f"""
You are a code generation assistant. Generate Python code based on the following:

Task: {task_description}
Library: {library}

Official Documentation:
{documentation}

Requirements:
- Use the latest API patterns from the documentation
- Include type hints
- Add brief comments for clarity
- Follow best practices
- Generate production-ready code

Generate only the code, no explanations.
        """

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Python developer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content
```

### Agent Card

```python
# agent_card.py
from a2a import AgentCard, Capability, Skill

def create_agent_card():
    return AgentCard(
        id="code-gen-agent",
        name="Context7-Powered Code Generator",
        description="Generates code using real-time documentation via Context7 MCP",
        version="1.0.0",

        capabilities=Capability(
            streaming=False,
            multi_turn=True,
            file_upload=[]
        ),

        skills=[
            Skill(
                name="generate-code",
                description="Generate code using specified library with up-to-date docs",
                input_schema={
                    "type": "object",
                    "properties": {
                        "library": {
                            "type": "string",
                            "description": "Library name (e.g., 'langchain', 'fastapi', 'a2a-sdk')"
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
                        "library_version": {"type": "string"}
                    }
                }
            )
        ],

        endpoints={
            "primary": "https://code-gen.example.com/agent"
        }
    )
```

### 클라이언트 사용 예제

```python
# client.py
import httpx
import json

async def request_code_generation():
    """Context7 기반 코드 생성 에이전트에 요청"""

    async with httpx.AsyncClient() as client:
        # 1. Agent Card 조회
        card_response = await client.get(
            "https://code-gen.example.com/.well-known/agent-card"
        )
        agent_card = card_response.json()

        print(f"Connected to: {agent_card['name']}")
        print(f"Skills: {[s['name'] for s in agent_card['skills']]}")

        # 2. 코드 생성 요청
        rpc_request = {
            "jsonrpc": "2.0",
            "method": "SendMessage",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "type": "text",
                            "text": "Generate code using langchain for a RAG agent with ChromaDB vector store"
                        }
                    ]
                }
            },
            "id": 1
        }

        response = await client.post(
            agent_card['endpoints']['primary'] + "/rpc",
            json=rpc_request
        )

        result = response.json()
        task = result['result']

        # 3. 생성된 코드 출력
        code_response = task['output']['parts'][0]['text']
        print("\nGenerated Code:")
        print(code_response)

        return task

# 사용
await request_code_generation()
```

### 실행 결과

```
Connected to: Context7-Powered Code Generator
Skills: ['generate-code']

Generated Code:
```python
from langchain.agents import create_retrieval_agent
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.tools.retriever import create_retriever_tool
from langchain.schema import Document
from typing import List

def create_rag_agent(
    documents: List[Document],
    persist_directory: str = "./chroma_db"
) -> Any:
    """
    ChromaDB를 벡터 스토어로 사용하는 RAG 에이전트 생성

    Args:
        documents: 인덱싱할 문서 리스트
        persist_directory: ChromaDB 영구 저장 디렉토리

    Returns:
        설정된 RAG 에이전트
    """
    # 임베딩 모델 초기화
    embeddings = OpenAIEmbeddings()

    # ChromaDB 벡터 스토어 생성
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    # Retriever 생성
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    # Retriever 도구 생성
    retriever_tool = create_retriever_tool(
        retriever=retriever,
        name="knowledge_base",
        description="Search the knowledge base for relevant information"
    )

    # LLM 초기화
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    # RAG 에이전트 생성
    agent = create_retrieval_agent(
        llm=llm,
        tools=[retriever_tool]
    )

    return agent

# 사용 예시
if __name__ == "__main__":
    # 문서 준비
    docs = [
        Document(page_content="Example content 1", metadata={"source": "doc1"}),
        Document(page_content="Example content 2", metadata={"source": "doc2"})
    ]

    # 에이전트 생성
    agent = create_rag_agent(docs)

    # 쿼리 실행
    response = agent.invoke({"input": "Tell me about the content"})
    print(response["output"])
```

Generated using langchain documentation from Context7 MCP.
```

### 멀티 에이전트 협업: Context7 + A2A

```python
# multi_agent_workflow.py
class MultiAgentCodeWorkflow:
    """여러 A2A 에이전트가 Context7를 활용해 협업하는 워크플로우"""

    async def generate_full_stack_app(self, requirements: str):
        """
        풀스택 애플리케이션 생성:
        1. Backend Agent: FastAPI로 백엔드 생성 (Context7 문서 사용)
        2. Frontend Agent: React로 프론트엔드 생성 (Context7 문서 사용)
        3. Integration Agent: 통합 및 배포 스크립트 생성
        """

        # 1. 백엔드 생성 요청
        backend_task = await self.call_agent(
            agent="backend-gen-agent",
            message=f"Generate code using fastapi for {requirements}"
        )

        # 2. 프론트엔드 생성 요청
        frontend_task = await self.call_agent(
            agent="frontend-gen-agent",
            message=f"Generate code using react for {requirements}"
        )

        # 3. 결과 통합
        integration = await self.call_agent(
            agent="integration-agent",
            message=f"Create integration scripts for backend and frontend"
        )

        return {
            "backend": backend_task['output'],
            "frontend": frontend_task['output'],
            "integration": integration['output']
        }

    async def call_agent(self, agent: str, message: str):
        """A2A 에이전트 호출 헬퍼"""
        # Agent registry에서 엔드포인트 조회
        agent_url = await self.lookup_agent(agent)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{agent_url}/rpc",
                json={
                    "jsonrpc": "2.0",
                    "method": "SendMessage",
                    "params": {
                        "message": {
                            "role": "user",
                            "parts": [{"type": "text", "text": message}]
                        }
                    },
                    "id": 1
                }
            )

            return response.json()['result']
```

### 핵심 포인트

1. **최신 문서 보장**: Context7 MCP를 통해 항상 최신 라이브러리 문서 활용
2. **캐싱 전략**: 동일한 라이브러리/쿼리에 대한 중복 호출 방지
3. **에러 처리**: Context7 호출 실패 시 폴백 메커니즘 구현
4. **멀티 에이전트**: 여러 A2A 에이전트가 Context7를 공유하여 협업
5. **버전 관리**: 특정 라이브러리 버전 문서 지정 가능

### 성능 최적화

```python
# 문서 캐싱 및 배치 처리
class OptimizedContext7Client:
    def __init__(self):
        self.cache = {}
        self.batch_requests = []

    async def batch_query_docs(
        self,
        queries: List[tuple[str, str]]
    ) -> Dict[str, str]:
        """여러 문서를 한 번에 쿼리"""
        results = {}

        # 캐시 확인
        for library_id, query in queries:
            cache_key = f"{library_id}:{query}"
            if cache_key in self.cache:
                results[cache_key] = self.cache[cache_key]
            else:
                self.batch_requests.append((library_id, query))

        # 배치 요청 실행
        if self.batch_requests:
            batch_results = await self._execute_batch()
            results.update(batch_results)

        return results
```

## 참고 자료

- [A2A Protocol Overview](./a2a-protocol-overview.md)
- [A2A Architecture](./a2a-architecture.md)
- [A2A Implementation Guide](./a2a-implementation-guide.md)
- [공식 샘플 저장소](https://github.com/a2aproject/a2a-samples)
