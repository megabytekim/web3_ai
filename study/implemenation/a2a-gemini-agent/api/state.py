# api/state.py
"""Shared state between A2A executor and Soul Store."""

from google import genai
from google.genai import types as genai_types

# Module-level singletons
gemini_client: genai.Client = genai.Client()
chat_histories: dict[str, list[genai_types.Content]] = {}
