"""Integration tests for the /api/soul-vault endpoint."""

import base64
import json
import time

import pytest
from starlette.testclient import TestClient


@pytest.fixture
def client():
    from api.index import app
    return TestClient(app)


def test_soul_vault_requires_ctx(client):
    resp = client.get("/api/soul-vault")
    assert resp.status_code == 400
    assert "ctx parameter required" in resp.json()["error"]


def test_soul_vault_unknown_ctx_returns_404(client):
    resp = client.get("/api/soul-vault?ctx=nonexistent")
    assert resp.status_code == 404
    assert "conversation not found" in resp.json()["error"]


def test_soul_vault_returns_402_without_payment(client):
    from api.state import chat_histories
    from google.genai import types as genai_types

    chat_histories["test_ctx"] = [
        genai_types.Content(role="user", parts=[genai_types.Part(text="hello")]),
    ]

    resp = client.get("/api/soul-vault?ctx=test_ctx")
    assert resp.status_code == 402
    assert "payment-required" in resp.headers


def test_soul_vault_options_returns_204(client):
    resp = client.options("/api/soul-vault")
    assert resp.status_code == 204
    assert "PAYMENT-SIGNATURE" in resp.headers.get("access-control-allow-headers", "")


def test_soul_vault_200_with_valid_payment(client):
    """Valid payment signature should return 200 with item, summary, and PAYMENT-RESPONSE header."""
    from unittest.mock import AsyncMock, MagicMock

    from api.state import chat_histories, gemini_client
    from api.x402 import PAY_TO, PRICE
    from google.genai import types as genai_types

    chat_histories["pay_ctx"] = [
        genai_types.Content(role="user", parts=[genai_types.Part(text="hello")]),
        genai_types.Content(role="model", parts=[genai_types.Part(text="hi there")]),
    ]

    # Mock Gemini summarization
    mock_response = MagicMock()
    mock_response.text = "자네의 대화는 짧았지만 깊었네..."
    gemini_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    # Build valid V2 payment signature
    payload = {
        "x402Version": 2,
        "accepted": {
            "scheme": "exact",
            "network": "eip155:84532",
            "amount": PRICE,
            "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
            "payTo": PAY_TO,
        },
        "payload": {
            "signature": "0xFAKESIG",
            "authorization": {
                "from": "0xPAYER_ADDR",
                "to": PAY_TO,
                "value": PRICE,
                "validAfter": 0,
                "validBefore": int(time.time()) + 3600,
                "nonce": "0x1234",
            },
        },
    }
    sig_b64 = base64.b64encode(json.dumps(payload).encode()).decode()

    resp = client.get(
        "/api/soul-vault?ctx=pay_ctx",
        headers={"PAYMENT-SIGNATURE": sig_b64},
    )
    assert resp.status_code == 200

    # Check response body structure
    data = resp.json()
    assert "item" in data
    assert data["item"]["name"] in ("영혼석", "금고", "수정구", "불사조의 깃털", "네오의 선글라스")
    assert data["item"]["rarity"] in ("common", "uncommon", "rare", "epic", "legendary")
    assert "emoji" in data["item"]
    assert "color" in data["item"]
    assert data["summary"] == "자네의 대화는 짧았지만 깊었네..."
    assert "payment" in data
    assert data["payment"]["network"] == "eip155:84532"

    # Check PAYMENT-RESPONSE header
    assert "payment-response" in resp.headers
    pr = json.loads(base64.b64decode(resp.headers["payment-response"]))
    assert pr["success"] is True
    assert pr["payer"] == "0xPAYER_ADDR"


def test_soul_vault_rejects_invalid_payment(client):
    """Malformed PAYMENT-SIGNATURE should return 400."""
    from api.state import chat_histories
    from google.genai import types as genai_types

    chat_histories["bad_pay_ctx"] = [
        genai_types.Content(role="user", parts=[genai_types.Part(text="hi")]),
    ]

    resp = client.get(
        "/api/soul-vault?ctx=bad_pay_ctx",
        headers={"PAYMENT-SIGNATURE": "not-valid-base64!!!"},
    )
    assert resp.status_code == 400
    assert "invalid payment signature" in resp.json()["error"]
