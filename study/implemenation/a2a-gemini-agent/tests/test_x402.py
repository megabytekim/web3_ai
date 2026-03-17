"""Tests for x402 V2 protocol simulation."""

import base64
import json
import time

import pytest


def _make_v2_payload(from_addr="0xPAYER_ADDRESS", to=None, value=None, valid_before=None):
    """Helper to build a V2-compliant PaymentPayload."""
    from api.x402 import NETWORK, PAY_TO, PRICE

    return {
        "x402Version": 2,
        "accepted": {
            "scheme": "exact",
            "network": NETWORK,
            "amount": PRICE,
            "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
            "payTo": to or PAY_TO,
        },
        "payload": {
            "signature": "0xFAKESIG",
            "authorization": {
                "from": from_addr,
                "to": to or PAY_TO,
                "value": value or PRICE,
                "validAfter": 0,
                "validBefore": valid_before or int(time.time()) + 3600,
                "nonce": "0x1234",
            },
        },
    }


def _encode(payload):
    return base64.b64encode(json.dumps(payload).encode()).decode()


def test_create_payment_required_response_returns_402():
    from api.x402 import create_payment_required_response

    response = create_payment_required_response()
    assert response.status_code == 402
    assert "payment-required" in response.headers


def test_payment_required_header_v2_structure():
    """PAYMENT-REQUIRED header should have V2 fields: resource, accepts[].amount."""
    from api.x402 import create_payment_required_response

    response = create_payment_required_response()
    header_value = response.headers["payment-required"]
    decoded = json.loads(base64.b64decode(header_value))

    assert decoded["x402Version"] == 2
    # V2: resource object at top level
    assert "resource" in decoded
    assert "url" in decoded["resource"]
    # V2: accepts[].amount (not maxAmountRequired)
    accept = decoded["accepts"][0]
    assert accept["scheme"] == "exact"
    assert accept["network"] == "eip155:84532"
    assert "amount" in accept
    assert "maxAmountRequired" not in accept  # V1 field should NOT be present
    assert "payTo" in accept
    assert "asset" in accept


def test_verify_valid_payment_signature():
    from api.x402 import verify_payment_signature

    payload = _make_v2_payload()
    result = verify_payment_signature(_encode(payload))
    assert result == "0xPAYER_ADDRESS"


def test_verify_rejects_wrong_recipient():
    from api.x402 import verify_payment_signature

    payload = _make_v2_payload(to="0xWRONG_ADDRESS")
    assert verify_payment_signature(_encode(payload)) is None


def test_verify_rejects_insufficient_amount():
    from api.x402 import verify_payment_signature

    payload = _make_v2_payload(value="1")
    assert verify_payment_signature(_encode(payload)) is None


def test_verify_rejects_expired_payment():
    from api.x402 import verify_payment_signature

    payload = _make_v2_payload(valid_before=int(time.time()) - 100)
    assert verify_payment_signature(_encode(payload)) is None


def test_verify_rejects_malformed_base64():
    from api.x402 import verify_payment_signature

    assert verify_payment_signature("not-valid-base64!!!") is None


def test_verify_rejects_missing_fields():
    from api.x402 import verify_payment_signature

    # V1 structure (scheme at top level) should be rejected
    payload = {"scheme": "exact", "network": "eip155:84532"}
    assert verify_payment_signature(_encode(payload)) is None


def test_create_payment_response_v2_fields():
    """PAYMENT-RESPONSE should use V2 field name 'transaction' (not 'tx_hash')."""
    from api.x402 import create_payment_response

    result = create_payment_response("0xPAYER")
    decoded = json.loads(base64.b64decode(result))
    assert decoded["success"] is True
    assert decoded["network"] == "eip155:84532"
    assert decoded["payer"] == "0xPAYER"
    assert decoded["transaction"].startswith("0x")  # V2: 'transaction'
    assert "tx_hash" not in decoded  # V1 field should NOT be present
