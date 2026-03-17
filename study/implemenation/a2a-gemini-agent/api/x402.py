"""x402 V2 protocol simulation for Soul Store.

Follows the official x402 V2 specification:
- https://github.com/coinbase/x402/blob/main/specs/x402-specification-v2.md
- https://github.com/coinbase/x402/blob/main/specs/transports-v2/http.md
"""

import base64
import json
import secrets
import time

from starlette.responses import Response

# x402 V2 Protocol Constants
NETWORK = "eip155:84532"  # Base Sepolia (CAIP-2)
ASSET = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"  # USDC on Base Sepolia
PAY_TO = "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18"  # Simulated receiver
PRICE = "100000"  # 0.10 USDC (6 decimals)


def create_payment_required_response() -> Response:
    """Return a 402 response with PAYMENT-REQUIRED header (x402 V2 format).

    V2 structure:
    - resource: describes what is being paid for
    - accepts[]: payment options the server will accept
    - accepts[].amount: replaces V1's maxAmountRequired
    """
    payment_required = {
        "x402Version": 2,
        "resource": {
            "url": "/api/soul-vault",
            "description": "Soul Store — store your conversation in a magical item",
            "mimeType": "application/json",
        },
        "accepts": [
            {
                "scheme": "exact",
                "payTo": PAY_TO,
                "amount": PRICE,
                "asset": ASSET,
                "network": NETWORK,
                "maxTimeoutSeconds": 3600,
                "extra": {"name": "USDC", "version": "2"},
            }
        ],
    }
    encoded = base64.b64encode(json.dumps(payment_required).encode()).decode()
    return Response(
        content=json.dumps({"error": "Payment Required", "x402Version": 2}),
        status_code=402,
        media_type="application/json",
        headers={"PAYMENT-REQUIRED": encoded},
    )


def verify_payment_signature(header_value: str) -> str | None:
    """Verify a PAYMENT-SIGNATURE header (simulated).

    V2 PaymentPayload structure:
    {
      x402Version: 2,
      accepted: { scheme, network, amount, asset, payTo, ... },
      payload: { signature, authorization: { from, to, value, ... } }
    }

    Returns the payer address if valid, None otherwise.
    """
    try:
        decoded = json.loads(base64.b64decode(header_value))
    except Exception:
        return None

    try:
        # V2: scheme/network are inside 'accepted', not at top level
        accepted = decoded["accepted"]
        payload = decoded["payload"]
        auth = payload["authorization"]

        if accepted.get("scheme") != "exact":
            return None
        if accepted.get("network") != NETWORK:
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
    """Create a base64-encoded PAYMENT-RESPONSE header value (SettlementResponse).

    V2 field name: 'transaction' (not 'tx_hash').
    """
    response_data = {
        "success": True,
        "network": NETWORK,
        "transaction": "0x" + secrets.token_hex(32),
        "payer": payer,
    }
    return base64.b64encode(json.dumps(response_data).encode()).decode()
