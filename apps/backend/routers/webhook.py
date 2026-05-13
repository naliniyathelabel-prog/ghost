from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx, os, logging

from db import get_supabase
from services.ai import generate_reply

router = APIRouter(prefix="/webhook")
logger = logging.getLogger(__name__)

BRIDGE_SECRET = os.getenv("BRIDGE_SECRET", "change-me")
BRIDGE_URL    = os.getenv("BRIDGE_URL", "http://localhost:3001")


class InboundMessage(BaseModel):
    from_: str
    text: str
    timestamp: int

    class Config:
        populate_by_name = True
        fields = {"from_": "from"}


async def _get_ghost_profile(user_id: str) -> dict | None:
    db = get_supabase()
    r = db.table("ghost_profiles").select("*").eq("user_id", user_id).single().execute()
    return r.data if r.data else None


async def _get_conversation_history(user_id: str, contact_phone: str, limit: int = 10) -> list:
    db = get_supabase()
    r = (
        db.table("message_logs")
        .select("direction,text")
        .eq("user_id", user_id)
        .eq("contact_phone", contact_phone)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    rows = list(reversed(r.data or []))
    return [
        {"role": "user" if row["direction"] == "inbound" else "assistant", "content": row["text"]}
        for row in rows
    ]


async def _log_message(user_id: str, contact_phone: str, direction: str, text: str, ai_generated: bool = False):
    db = get_supabase()
    db.table("message_logs").insert({
        "user_id": user_id,
        "contact_phone": contact_phone,
        "direction": direction,
        "text": text,
        "ai_generated": ai_generated,
    }).execute()


async def _send_via_bridge(to: str, text: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BRIDGE_URL}/send",
            json={"to": to, "text": text},
            headers={"x-bridge-secret": BRIDGE_SECRET},
            timeout=15,
        )
        r.raise_for_status()


async def _get_contact_policy(user_id: str, phone: str) -> str:
    db = get_supabase()
    r = (
        db.table("contacts")
        .select("policy")
        .eq("user_id", user_id)
        .eq("phone", phone)
        .single()
        .execute()
    )
    return r.data["policy"] if r.data else "auto"


@router.post("/inbound")
async def inbound(msg: InboundMessage, x_bridge_secret: Optional[str] = Header(None)):
    if x_bridge_secret != BRIDGE_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 1. Resolve user_id from bridge (bridge sends on behalf of one user for MVP)
    user_id = os.getenv("GHOST_USER_ID", "")
    if not user_id:
        logger.warning("GHOST_USER_ID not set — cannot process inbound")
        return {"received": True, "processed": False, "reason": "no user configured"}

    # 2. Log inbound
    await _log_message(user_id, msg.from_, "inbound", msg.text)

    # 3. Check Ghost is active
    profile = await _get_ghost_profile(user_id)
    if not profile or not profile.get("active"):
        return {"received": True, "processed": False, "reason": "ghost inactive"}

    # 4. Check contact policy
    policy = await _get_contact_policy(user_id, msg.from_)
    if policy == "never":
        return {"received": True, "processed": False, "reason": "contact policy=never"}
    if policy == "ask":
        # TODO: push notification to mobile — user decides
        return {"received": True, "processed": False, "reason": "contact policy=ask — awaiting user"}

    # 5. Build conversation history
    history = await _get_conversation_history(user_id, msg.from_)

    # 6. Generate AI reply
    tier = profile.get("tier", "free")
    reply = await generate_reply(profile, history, msg.text, tier=tier)

    # 7. Send via bridge
    await _send_via_bridge(msg.from_, reply)

    # 8. Log outbound
    await _log_message(user_id, msg.from_, "outbound", reply, ai_generated=True)

    logger.info(f"Ghost replied to {msg.from_}: {reply[:60]}...")
    return {"received": True, "processed": True, "reply_preview": reply[:80]}
