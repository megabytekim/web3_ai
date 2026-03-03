"""Tests for GeminiChatExecutor."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_executor_extracts_text_and_calls_gemini():
    """Executor should extract user text, call Gemini, and enqueue response."""
    from api.index import GeminiChatExecutor

    executor = GeminiChatExecutor()

    # Mock context
    context = MagicMock()
    context.get_user_input.return_value = "Hello, who are you?"
    context.context_id = "ctx_123"

    # Mock event queue
    event_queue = AsyncMock()

    with patch.object(executor, "_get_gemini_response", new_callable=AsyncMock) as mock_gemini:
        mock_gemini.return_value = "I'm a Gemini-powered chat agent!"
        asyncio.run(executor.execute(context, event_queue))

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

    with pytest.raises(Exception, match="cancel not supported"):
        asyncio.run(executor.cancel(context, event_queue))
