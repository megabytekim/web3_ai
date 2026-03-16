"""Soul Store — item gacha system and conversation summarization."""

import random

from google.genai import types as genai_types

ITEMS = [
    {"name": "영혼석", "rarity": "common", "weight": 50, "emoji": "💎", "color": "#ffffff"},
    {"name": "금고", "rarity": "uncommon", "weight": 25, "emoji": "🗄️", "color": "#00ff41"},
    {"name": "수정구", "rarity": "rare", "weight": 15, "emoji": "🔮", "color": "#4169e1"},
    {"name": "불사조의 깃털", "rarity": "epic", "weight": 8, "emoji": "🪶", "color": "#9b59b6"},
    {"name": "네오의 선글라스", "rarity": "legendary", "weight": 2, "emoji": "🕶️", "color": "#ffd700"},
]

_WEIGHTS = [item["weight"] for item in ITEMS]

SUMMARIZE_MODEL = "gemma-3-27b-it"

SUMMARIZE_PROMPT = """아래 대화를 Agent M(모피어스) 말투로 3줄 이내로 요약해줘.
마치 영혼석이나 수정구에 새겨넣을 비문처럼 간결하고 여운 있게.

대화 내용:
"""


def draw_item() -> dict:
    """Draw a random item based on weighted probability."""
    chosen = random.choices(ITEMS, weights=_WEIGHTS, k=1)[0]
    return {
        "name": chosen["name"],
        "rarity": chosen["rarity"],
        "emoji": chosen["emoji"],
        "color": chosen["color"],
    }


async def summarize_conversation(
    client,
    history: list[genai_types.Content],
) -> str:
    """Summarize a conversation using Gemini, in Agent M's voice."""
    lines = []
    for content in history:
        role = "사용자" if content.role == "user" else "Agent M"
        text = content.parts[0].text if content.parts else ""
        if text.startswith("[시스템 지시]"):
            continue
        lines.append(f"{role}: {text}")

    conversation_text = "\n".join(lines)

    try:
        response = await client.aio.models.generate_content(
            model=SUMMARIZE_MODEL,
            contents=[
                genai_types.Content(
                    role="user",
                    parts=[genai_types.Part(text=SUMMARIZE_PROMPT + conversation_text)],
                )
            ],
        )
        return response.text or "(영혼의 기록을 해독할 수 없었네...)"
    except Exception:
        return "(영혼의 기록을 해독할 수 없었네...)"
