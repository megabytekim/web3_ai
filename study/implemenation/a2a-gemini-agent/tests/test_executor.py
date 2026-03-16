"""Tests for GeminiChatExecutor."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_executor_extracts_text_and_calls_gemini():
    """Executor should extract user text, call Gemini, and enqueue response."""
    from google.genai import types as genai_types

    from api.index import GeminiChatExecutor

    executor = GeminiChatExecutor()

    # Configure the mock client to return a proper response
    mock_response = MagicMock()
    mock_response.text = "I'm a Gemini-powered chat agent!"
    executor._client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    # Mock context
    context = MagicMock()
    context.get_user_input.return_value = "Hello, who are you?"
    context.context_id = "ctx_123"

    # Mock event queue
    event_queue = AsyncMock()

    asyncio.run(executor.execute(context, event_queue))

    # Verify Gemini was called
    executor._client.aio.models.generate_content.assert_called_once()

    # Verify history: 2 system prompt turns + 1 user + 1 model = 4
    history = executor._chat_histories["ctx_123"]
    assert len(history) == 4
    assert isinstance(history[0], genai_types.Content)
    assert history[0].role == "user"   # system prompt injected as user turn
    assert history[1].role == "model"  # fake model ack
    assert history[2].role == "user"   # actual user message
    assert history[3].role == "model"  # gemini response

    # Verify the response was enqueued
    event_queue.enqueue_event.assert_called_once()
    call_args = event_queue.enqueue_event.call_args[0][0]
    assert call_args.parts[0].root.text == "I'm a Gemini-powered chat agent!"


def test_executor_maintains_separate_contexts():
    """Different contextIds should have separate chat histories."""
    from api.index import GeminiChatExecutor

    executor = GeminiChatExecutor()
    assert executor._chat_histories == {}

    # Simulate adding history for two contexts
    executor._chat_histories["ctx_1"] = [{"role": "user", "text": "hi"}]
    executor._chat_histories["ctx_2"] = [{"role": "user", "text": "hello"}]

    assert len(executor._chat_histories) == 2
    assert executor._chat_histories["ctx_1"] != executor._chat_histories["ctx_2"]


def test_cancel_raises():
    """Cancel should raise an exception (not supported)."""
    from api.index import GeminiChatExecutor

    executor = GeminiChatExecutor()
    context = MagicMock()
    event_queue = AsyncMock()

    from a2a.utils.errors import ServerError

    with pytest.raises(ServerError):
        asyncio.run(executor.cancel(context, event_queue))


def test_executor_replaces_soul_store_link():
    """SOUL_STORE_LINK in Gemini response should be replaced with actual URL."""
    import asyncio
    from unittest.mock import AsyncMock, MagicMock
    from api.index import GeminiChatExecutor

    executor = GeminiChatExecutor()

    mock_response = MagicMock()
    mock_response.text = "자네의 깨달음을 담아두게... [영혼 저장소](SOUL_STORE_LINK)"
    executor._client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    context = MagicMock()
    context.get_user_input.return_value = "이 대화를 간직하고 싶어"
    context.context_id = "ctx_abc"

    event_queue = AsyncMock()

    asyncio.run(executor.execute(context, event_queue))

    call_args = event_queue.enqueue_event.call_args[0][0]
    assert "/soul-store?ctx=ctx_abc" in call_args.parts[0].root.text
    assert "SOUL_STORE_LINK" not in call_args.parts[0].root.text
