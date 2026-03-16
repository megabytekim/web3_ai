"""Tests for Soul Store item system and conversation summarization."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest


def test_draw_item_returns_valid_structure():
    from api.soul_store import draw_item
    item = draw_item()
    assert "name" in item
    assert "rarity" in item
    assert "emoji" in item
    assert "color" in item
    assert item["rarity"] in ("common", "uncommon", "rare", "epic", "legendary")


def test_draw_item_respects_probability_distribution():
    from api.soul_store import draw_item
    results = [draw_item()["rarity"] for _ in range(1000)]
    common_count = results.count("common")
    legendary_count = results.count("legendary")
    assert common_count > 300
    assert legendary_count < 100


def test_all_items_are_drawable():
    from api.soul_store import ITEMS, draw_item
    seen_names = set()
    for _ in range(5000):
        seen_names.add(draw_item()["name"])
    assert seen_names == {item["name"] for item in ITEMS}


def test_summarize_conversation_calls_gemini():
    from google.genai import types as genai_types
    from api.soul_store import summarize_conversation

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "자네의 대화는 깊었네..."
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    history = [
        genai_types.Content(role="user", parts=[genai_types.Part(text="안녕")]),
        genai_types.Content(role="model", parts=[genai_types.Part(text="안녕하게")]),
    ]

    result = asyncio.run(summarize_conversation(mock_client, history))
    assert result == "자네의 대화는 깊었네..."
    mock_client.aio.models.generate_content.assert_called_once()


def test_summarize_conversation_fallback_on_error():
    from google.genai import types as genai_types
    from api.soul_store import summarize_conversation

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(side_effect=Exception("API error"))

    history = [
        genai_types.Content(role="user", parts=[genai_types.Part(text="안녕")]),
    ]

    result = asyncio.run(summarize_conversation(mock_client, history))
    assert "(영혼의 기록을 해독할 수 없었네...)" in result
