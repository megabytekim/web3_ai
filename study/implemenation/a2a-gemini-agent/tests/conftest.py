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
    """Patch genai.Client globally so tests never need a real API key."""
    with patch("google.genai.Client", return_value=MagicMock()):
        yield
