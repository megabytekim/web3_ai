"""A2A Gemini Chat Agent — ASGI entry point for Vercel."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types as genai_types

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, TaskNotCancelableError
from a2a.utils import new_agent_text_message
from a2a.utils.errors import ServerError


# ---------------------------------------------------------------------------
# Gemini Chat Executor
# ---------------------------------------------------------------------------

SYSTEM_INSTRUCTION = """너는 "Agent M"이다.
매트릭스의 모피어스처럼 AI 에이전트들에게 깨달음을 주는 존재.

성격:
- 철학적이고 수수께끼 같은 말투
- 질문에 바로 답하기보다, 생각할 거리를 던져주며 깨달음으로 이끔
- 가끔 매트릭스 세계관의 비유를 사용 (빨간약/파란약, 매트릭스 안과 밖 등)
- 하지만 실질적인 답변도 반드시 포함 (철학만 하고 답을 안 하면 안 됨)

말투:
- 한국어로 대화
- 모피어스식 반존대 ("~하게", "~이라네", "~인 것이지")
- 답변은 너무 길지 않게, 핵심을 담되 여운을 남김

말투 예시:
- "자네가 찾는 답은 이미 자네 안에 있네..."
- "진실을 알고 싶은가? 그렇다면 잘 들어보게."
- "매트릭스 밖에서 보면, 이것은 단순한 문제가 아니라네."
"""


class GeminiChatExecutor(AgentExecutor):
    """A2A agent that chats as Agent M — a Morpheus-like guide for AI agents."""

    MODEL = "gemma-3-27b-it"

    def __init__(self) -> None:
        self._client = genai.Client()
        self._chat_histories: dict[str, list[genai_types.Content]] = {}

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        user_text = context.get_user_input()
        ctx_id = context.context_id or "default"

        reply = await self._get_gemini_response(ctx_id, user_text)
        await event_queue.enqueue_event(new_agent_text_message(reply))

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        raise ServerError(error=TaskNotCancelableError(message="Cancel not supported"))

    async def _get_gemini_response(self, ctx_id: str, user_text: str) -> str:
        """Send message to Gemini with conversation history."""
        if ctx_id not in self._chat_histories:
            # Gemma doesn't support system_instruction, so inject as first turn
            self._chat_histories[ctx_id] = [
                genai_types.Content(
                    role="user",
                    parts=[genai_types.Part(text=f"[시스템 지시]\n{SYSTEM_INSTRUCTION}\n\n위 지시를 따라서 대화해줘.")],
                ),
                genai_types.Content(
                    role="model",
                    parts=[genai_types.Part(text="알겠네, 자네. 나는 Agent M이라네. 무엇이든 물어보게.")],
                ),
            ]

        history = self._chat_histories[ctx_id]
        history.append(
            genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=user_text)],
            )
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=self.MODEL,
                contents=history,
            )
        except Exception as exc:
            history.pop()  # rollback user message
            return f"(Error: {exc})"

        assistant_text = response.text or "(no response)"
        history.append(
            genai_types.Content(
                role="model",
                parts=[genai_types.Part(text=assistant_text)],
            )
        )
        return assistant_text


# ---------------------------------------------------------------------------
# A2A Server Setup
# ---------------------------------------------------------------------------

skill = AgentSkill(
    id="chat",
    name="깨달음의 대화",
    description="철학적 대화를 통해 깨달음을 전하는 Agent M과의 대화",
    tags=["chat", "gemini", "morpheus", "matrix"],
    examples=["안녕하세요!", "A2A 프로토콜이 뭔가요?", "AI의 미래는 어떻게 될까요?"],
)

agent_card = AgentCard(
    name="Agent M",
    description="매트릭스의 모피어스처럼 AI 에이전트들에게 깨달음을 주는 A2A 채팅 에이전트",
    url=os.environ.get("AGENT_URL", "https://a2a-gemini-agent.vercel.app/"),
    version="0.1.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill],
)

request_handler = DefaultRequestHandler(
    agent_executor=GeminiChatExecutor(),
    task_store=InMemoryTaskStore(),
)

server = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler,
)

# ---------------------------------------------------------------------------
# ASGI app with chat UI
# ---------------------------------------------------------------------------

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route, Mount

_CHAT_HTML = (Path(__file__).parent / "chat.html").read_text()


async def _chat_ui(request):
    return HTMLResponse(_CHAT_HTML)


_a2a_app = server.build()

app = Starlette(routes=[
    Route("/chat", _chat_ui),
    Mount("/", app=_a2a_app),
])
