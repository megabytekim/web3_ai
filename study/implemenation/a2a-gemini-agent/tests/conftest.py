"""Shared test fixtures for a2a-gemini-agent tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure the project root is on sys.path so `from api.index import ...` works.
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Patch genai.Client at collection time so that api/state.py (which calls
# genai.Client() at module level) never contacts the real API during tests.
_client_patcher = patch("google.genai.Client", return_value=MagicMock())
_client_patcher.start()


@pytest.fixture(autouse=True)
def _mock_genai_client():
    """Patch genai.Client globally so tests never need a real API key."""
    mock_client = MagicMock()
    with patch("google.genai.Client", return_value=mock_client):
        yield


@pytest.fixture(autouse=True)
def _clear_chat_histories():
    """Clear shared chat_histories between tests."""
    from api.state import chat_histories
    chat_histories.clear()
    yield
    chat_histories.clear()
