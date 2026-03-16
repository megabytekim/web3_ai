"""Tests for x402 protocol simulation."""

import base64
import json
import time

import pytest


def test_create_payment_required_response_returns_402():
    from api.x402 import create_payment_required_response
    response = create_payment_required_response()
    assert response.status_code == 402
    assert "payment-required" in response.headers


def test_payment_required_header_is_valid_base64_json():
    from api.x402 import create_payment_required_response
    response = create_payment_required_response()
    header_value = response.headers["payment-required"]
    decoded = json.loads(base64.b64decode(header_value))
    assert decoded["x402Version"] == 2
    assert len(decoded["accepts"]) == 1
    accept = decoded["accepts"][0]
    assert accept["scheme"] == "exact"
    assert accept["network"] == "eip155:84532"
    assert "payTo" in accept
    assert "maxAmountRequired" in accept
    assert "asset" in accept


def test_verify_valid_payment_signature():
    from api.x402 import PAY_TO, PRICE, verify_payment_signature
    payload = {
        "scheme": "exact",
        "network": "eip155:84532",
        "payload": {
            "signature": "0xFAKESIG",
            "authorization": {
                "from": "0xPAYER_ADDRESS",
                "to": PAY_TO,
                "value": PRICE,
                "validAfter": 0,
                "validBefore": int(time.time()) + 3600,
                "nonce": "0x1234",
            },
        },
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    result = verify_payment_signature(encoded)
    assert result == "0xPAYER_ADDRESS"


def test_verify_rejects_wrong_recipient():
    from api.x402 import PRICE, verify_payment_signature
    payload = {
        "scheme": "exact",
        "network": "eip155:84532",
        "payload": {
            "signature": "0xFAKESIG",
            "authorization": {
                "from": "0xPAYER",
                "to": "0xWRONG_ADDRESS",
                "value": PRICE,
                "validAfter": 0,
                "validBefore": int(time.time()) + 3600,
                "nonce": "0x1234",
            },
        },
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    assert verify_payment_signature(encoded) is None


def test_verify_rejects_insufficient_amount():
    from api.x402 import PAY_TO, verify_payment_signature
    payload = {
        "scheme": "exact",
        "network": "eip155:84532",
        "payload": {
            "signature": "0xFAKESIG",
            "authorization": {
                "from": "0xPAYER",
                "to": PAY_TO,
                "value": "1",
                "validAfter": 0,
                "validBefore": int(time.time()) + 3600,
                "nonce": "0x1234",
            },
        },
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    assert verify_payment_signature(encoded) is None


def test_verify_rejects_expired_payment():
    from api.x402 import PAY_TO, PRICE, verify_payment_signature
    payload = {
        "scheme": "exact",
        "network": "eip155:84532",
        "payload": {
            "signature": "0xFAKESIG",
            "authorization": {
                "from": "0xPAYER",
                "to": PAY_TO,
                "value": PRICE,
                "validAfter": 0,
                "validBefore": int(time.time()) - 100,
                "nonce": "0x1234",
            },
        },
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    assert verify_payment_signature(encoded) is None


def test_verify_rejects_malformed_base64():
    from api.x402 import verify_payment_signature
    assert verify_payment_signature("not-valid-base64!!!") is None


def test_verify_rejects_missing_fields():
    from api.x402 import verify_payment_signature
    payload = {"scheme": "exact"}
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    assert verify_payment_signature(encoded) is None


def test_create_payment_response_returns_base64_json():
    from api.x402 import create_payment_response
    result = create_payment_response("0xPAYER")
    decoded = json.loads(base64.b64decode(result))
    assert decoded["success"] is True
    assert decoded["network"] == "eip155:84532"
    assert decoded["payer"] == "0xPAYER"
    assert decoded["tx_hash"].startswith("0x")
