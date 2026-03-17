"""Shared test fixtures for a2a-gemini-agent tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure the project root is on sys.path so `from api.index import ...` works.
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture(autouse=True)
def _mock_genai_client():
    """Patch genai.Client and reset lazy singleton so tests never need a real API key."""
    import api.state

    mock_client = MagicMock()
    api.state._gemini_client = mock_client
    with patch("google.genai.Client", return_value=mock_client):
        yield
    api.state._gemini_client = None


@pytest.fixture(autouse=True)
def _clear_chat_histories():
    """Clear shared chat_histories between tests."""
    from api.state import chat_histories
    chat_histories.clear()
    yield
    chat_histories.clear()
