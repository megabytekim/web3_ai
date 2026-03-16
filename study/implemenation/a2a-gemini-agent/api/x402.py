"""x402 V2 protocol simulation for Soul Store."""

import base64
import json
import secrets
import time

from starlette.responses import Response

# x402 V2 Protocol Constants
NETWORK = "eip155:84532"  # Base Sepolia
ASSET = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"  # USDC on Base Sepolia
PAY_TO = "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18"  # Simulated receiver
PRICE = "100000"  # 0.10 USDC (6 decimals)


def create_payment_required_response() -> Response:
    """Return a 402 response with PAYMENT-REQUIRED header (x402 V2 format)."""
    payment_requirements = {
        "x402Version": 2,
        "accepts": [
            {
                "scheme": "exact",
                "payTo": PAY_TO,
                "maxAmountRequired": PRICE,
                "asset": ASSET,
                "network": NETWORK,
                "extra": {"name": "USDC", "version": "2"},
            }
        ],
    }
    encoded = base64.b64encode(json.dumps(payment_requirements).encode()).decode()
    return Response(
        content=json.dumps({"error": "Payment Required", "x402Version": 2}),
        status_code=402,
        media_type="application/json",
        headers={"PAYMENT-REQUIRED": encoded},
    )


def verify_payment_signature(header_value: str) -> str | None:
    """Verify a PAYMENT-SIGNATURE header (simulated).
    Returns the payer address if valid, None otherwise.
    """
    try:
        decoded = json.loads(base64.b64decode(header_value))
    except Exception:
        return None

    try:
        payload = decoded["payload"]
        auth = payload["authorization"]

        if decoded.get("scheme") != "exact":
            return None
        if decoded.get("network") != NETWORK:
            return None
        if auth["to"] != PAY_TO:
            return None
        if int(auth["value"]) < int(PRICE):
            return None
        if auth["validBefore"] <= time.time():
            return None

        return auth["from"]
    except (KeyError, TypeError, ValueError):
        return None


def create_payment_response(payer: str) -> str:
    """Create a base64-encoded PAYMENT-RESPONSE header value."""
    response_data = {
        "success": True,
        "network": NETWORK,
        "tx_hash": "0x" + secrets.token_hex(32),
        "payer": payer,
    }
    return base64.b64encode(json.dumps(response_data).encode()).decode()
