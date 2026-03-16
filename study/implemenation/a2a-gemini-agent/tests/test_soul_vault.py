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
