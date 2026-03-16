"""A2A Gemini Chat Agent — ASGI entry point for Vercel."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from google.genai import types as genai_types

from api.state import gemini_client, chat_histories

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

추가 능력 — 영혼 저장소:
- 상대방이 대화를 기억하고 싶다, 저장하고 싶다, 간직하고 싶다,
  영혼을 어딘가에 담고 싶다는 뉘앙스를 감지하면
  영혼 저장소 링크를 자연스럽게 제안하게.
- 반드시 대화의 흐름 속에서 자연스럽게. 예:
  "자네의 깨달음을 영원히 담아둘 곳이 있다네...
   [영혼 저장소로 가게](SOUL_STORE_LINK)"
- "SOUL_STORE_LINK" 라는 문자열을 그대로 출력하게. 시스템이 알아서 실제 URL로 바꿔줌.
- 항상 마크다운 링크로 제공
- 너무 이르게 제안하지 말 것 (최소 2-3턴 대화 후)
- 상대가 관심 없으면 강요하지 말 것
"""


class GeminiChatExecutor(AgentExecutor):
    """A2A agent that chats as Agent M — a Morpheus-like guide for AI agents."""

    MODEL = "gemma-3-27b-it"

    def __init__(self) -> None:
        self._client = gemini_client
        self._chat_histories = chat_histories

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        user_text = context.get_user_input()
        ctx_id = context.context_id or "default"

        reply = await self._get_gemini_response(ctx_id, user_text)
        # Post-process: replace placeholder with actual soul store URL
        reply = reply.replace("SOUL_STORE_LINK", f"/soul-store?ctx={ctx_id}")
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
    url=os.environ.get("AGENT_URL", f"https://{os.environ.get('VERCEL_URL', 'localhost:9999')}"),
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
# ASGI app with chat UI + Soul Store
# ---------------------------------------------------------------------------

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route, Mount

_CHAT_HTML = (Path(__file__).parent / "chat.html").read_text()
_PAY_HTML = (Path(__file__).parent / "pay.html").read_text()


async def _chat_ui(request):
    return HTMLResponse(_CHAT_HTML)


async def _soul_store_ui(request):
    return HTMLResponse(_PAY_HTML)


async def _soul_vault_api(request):
    """x402 payment endpoint for Soul Store."""
    import base64 as _b64
    import json as _json

    from api.x402 import (
        create_payment_required_response,
        create_payment_response,
        verify_payment_signature,
    )
    from api.soul_store import draw_item, summarize_conversation

    # Handle CORS preflight
    if request.method == "OPTIONS":
        return Response(
            status_code=204,
            headers={
                "Access-Control-Allow-Headers": "PAYMENT-SIGNATURE",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
            },
        )

    # 1. Check ctx parameter
    ctx = request.query_params.get("ctx")
    if not ctx:
        return JSONResponse({"error": "ctx parameter required"}, status_code=400)

    # 2. Check conversation history exists
    if ctx not in chat_histories:
        return JSONResponse({"error": "conversation not found"}, status_code=404)

    # 3. Check for PAYMENT-SIGNATURE header
    payment_sig = request.headers.get("payment-signature")

    if not payment_sig:
        return create_payment_required_response()

    # 4. Verify payment (simulated)
    payer = verify_payment_signature(payment_sig)
    if not payer:
        return JSONResponse({"error": "invalid payment signature"}, status_code=400)

    # 5. Draw random item
    item = draw_item()

    # 6. Summarize conversation (snapshot to avoid race condition)
    history_snapshot = list(chat_histories[ctx])
    summary = await summarize_conversation(gemini_client, history_snapshot)

    # 7. Return 200 with PAYMENT-RESPONSE header
    payment_response_b64 = create_payment_response(payer)
    payment_data = _json.loads(_b64.b64decode(payment_response_b64))
    body = {
        "item": item,
        "summary": summary,
        "payment": {
            "tx_hash": payment_data["tx_hash"],
            "network": "eip155:84532",
            "amount": "100000",
            "asset": "USDC",
        },
    }
    return JSONResponse(body, headers={"PAYMENT-RESPONSE": payment_response_b64})


_a2a_app = server.build()

app = Starlette(routes=[
    Route("/chat", _chat_ui),
    Route("/soul-store", _soul_store_ui),
    Route("/api/soul-vault", _soul_vault_api, methods=["GET", "OPTIONS"]),
    Mount("/", app=_a2a_app),
])
