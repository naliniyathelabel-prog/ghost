from db.supabase_client import get_supabase
from typing import Optional, Dict, List

async def fetch_ghost_profile(user_id: str) -> Optional[Dict]:
    sb = get_supabase()
    r = sb.table("ghost_profiles").select("*").eq("user_id", user_id).single().execute()
    return r.data if r.data else None

async def fetch_conversation_history(user_id: str, contact_phone: str, limit: int = 10) -> List[Dict]:
    sb = get_supabase()
    r = (
        sb.table("message_logs")
        .select("direction, text")
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

async def log_message(user_id: str, contact_phone: str, direction: str, text: str, ai_generated: bool = False):
    sb = get_supabase()
    sb.table("message_logs").insert({
        "user_id": user_id,
        "contact_phone": contact_phone,
        "direction": direction,
        "text": text,
        "ai_generated": ai_generated,
    }).execute()

async def get_contact_policy(user_id: str, phone: str) -> str:
    """Returns: auto | ask | never"""
    sb = get_supabase()
    r = sb.table("contacts").select("policy").eq("user_id", user_id).eq("phone", phone).single().execute()
    return r.data["policy"] if r.data else "auto"
