# api/state.py
"""Shared state between A2A executor and Soul Store."""

from google import genai
from google.genai import types as genai_types

# Module-level singletons (lazy init for gemini_client)
_gemini_client: genai.Client | None = None
chat_histories: dict[str, list[genai_types.Content]] = {}
# Stores soul store results per ctx — consumed once by executor on next chat message
soul_store_results: dict[str, dict] = {}


def get_gemini_client() -> genai.Client:
    """Lazy-initialize Gemini client on first use."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client()
    return _gemini_client


# For backward compatibility — property-like access
class _LazyClient:
    """Proxy that delays genai.Client() creation until first attribute access."""

    def __getattr__(self, name):
        return getattr(get_gemini_client(), name)


gemini_client = _LazyClient()
