"""Simple test client for the A2A Gemini Chat Agent."""

import httpx
import uuid
import json

AGENT_URL = "http://localhost:9999"


def main():
    client = httpx.Client(timeout=30.0)

    # Step 1: Discover agent
    print("=== Agent Discovery ===")
    resp = client.get(f"{AGENT_URL}/.well-known/agent.json")
    card = resp.json()
    print(f"Name: {card['name']}")
    print(f"Skills: {[s['name'] for s in card['skills']]}")

    # Step 2: Send first message
    context_id = f"ctx_{uuid.uuid4().hex[:8]}"
    print(f"\n=== Chat (context: {context_id}) ===")

    messages = [
        "Hello! What can you do?",
        "Tell me a short joke.",
        "What was my first message to you?",  # tests multi-turn memory
    ]

    for msg in messages:
        print(f"\nUser: {msg}")
        result = send_message(client, context_id, msg)
        if result:
            # Extract agent response from task artifacts or status
            print(f"Agent: {json.dumps(result, indent=2, ensure_ascii=False)}")


def send_message(client: httpx.Client, context_id: str, text: str) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "contextId": context_id,
                "parts": [{"kind": "text", "text": text}],
            }
        },
    }
    resp = client.post(
        f"{AGENT_URL}/",
        json=payload,
        headers={"Content-Type": "application/json"},
    )
    return resp.json()


if __name__ == "__main__":
    main()
