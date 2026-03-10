"""A2A Gemini Chat Agent — ASGI entry point for Vercel."""

import os
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types as genai_types

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.utils import new_agent_text_message


# ---------------------------------------------------------------------------
# Gemini Chat Executor
# ---------------------------------------------------------------------------

class GeminiChatExecutor(AgentExecutor):
    """A2A agent that chats using Google Gemini with multi-turn history."""

    MODEL = "gemini-2.5-flash"

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
        raise Exception("cancel not supported")

    async def _get_gemini_response(self, ctx_id: str, user_text: str) -> str:
        """Send message to Gemini with conversation history."""
        if ctx_id not in self._chat_histories:
            self._chat_histories[ctx_id] = []

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
        except Exception:
            history.pop()  # rollback user message
            return "(Error: could not get response)"

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
    name="General Chat",
    description="General-purpose conversation powered by Google Gemini",
    tags=["chat", "gemini", "conversation"],
    examples=["Hello!", "Tell me about A2A protocol", "What can you do?"],
)

agent_card = AgentCard(
    name="Gemini Chat Agent",
    description="A2A agent that chats using Google Gemini with multi-turn context",
    url=os.environ.get("AGENT_URL", "http://localhost:9999/"),
    version="0.1.0",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
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

app = server.build()
