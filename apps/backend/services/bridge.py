import os, httpx
from typing import Optional

BRIDGE_URL    = os.getenv("BRIDGE_URL", "http://localhost:3001")
BRIDGE_SECRET = os.getenv("BRIDGE_SECRET", "change-me")

async def send_whatsapp(to: str, text: str) -> bool:
    """POST to Baileys bridge /send endpoint."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                f"{BRIDGE_URL}/send",
                json={"to": to, "text": text},
                headers={"x-bridge-secret": BRIDGE_SECRET},
            )
            r.raise_for_status()
            return True
    except Exception as e:
        # Log but don't crash — message will be retried manually via inbox
        print(f"[bridge] send failed to {to}: {e}")
        return False
