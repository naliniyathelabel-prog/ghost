from fastapi import APIRouter, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import os

from services.ghost import (
    fetch_ghost_profile,
    fetch_conversation_history,
    log_message,
    get_contact_policy,
)
from services.ai import generate_reply
from services.bridge import send_whatsapp

router = APIRouter(prefix="/webhook")

BRIDGE_SECRET = os.getenv("BRIDGE_SECRET", "change-me")

# Maps a WhatsApp JID (e.g. 919xxxxxxx@s.whatsapp.net) to E.164 phone string
def jid_to_phone(jid: str) -> str:
    return "+" + jid.replace("@s.whatsapp.net", "").replace("@g.us", "")


class InboundMessage(BaseModel):
    from_jid: str   # full WhatsApp JID from Baileys
    text: str
    timestamp: int

    class Config:
        populate_by_name = True
        fields = {"from_jid": "from"}


async def process_message(user_id: str, from_jid: str, text: str):
    """Background task: fetch profile → generate reply → send → log."""
    contact_phone = jid_to_phone(from_jid)

    # 1. Check contact policy
    policy = await get_contact_policy(user_id, contact_phone)
    if policy == "never":
        return
    # TODO: policy == "ask" → push notification to mobile, wait for approval

    # 2. Fetch ghost profile
    profile = await fetch_ghost_profile(user_id)
    if not profile or not profile.get("active"):
        return  # Ghost is toggled OFF

    # 3. Log inbound
    await log_message(user_id, contact_phone, "inbound", text, ai_generated=False)

    # 4. Fetch conversation history for context
    history = await fetch_conversation_history(user_id, contact_phone)

    # 5. Generate AI reply
    tier = profile.get("tier", "free")
    reply = await generate_reply(profile, history, text, tier=tier)

    # 6. Send via bridge
    sent = await send_whatsapp(from_jid, reply)

    # 7. Log outbound
    if sent:
        await log_message(user_id, contact_phone, "outbound", reply, ai_generated=True)


@router.post("/inbound")
async def inbound(
    msg: InboundMessage,
    background_tasks: BackgroundTasks,
    x_bridge_secret: Optional[str] = Header(None),
):
    if x_bridge_secret != BRIDGE_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # TODO: resolve user_id from bridge config / linked account
    # For MVP: single-user mode — bridge is tied to one account
    user_id = os.getenv("GHOST_USER_ID", "")
    if not user_id:
        raise HTTPException(status_code=500, detail="GHOST_USER_ID not configured")

    # Fire and forget — respond to bridge immediately, process async
    background_tasks.add_task(process_message, user_id, msg.from_jid, msg.text)
    return {"queued": True}
