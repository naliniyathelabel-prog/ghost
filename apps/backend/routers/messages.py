from fastapi import APIRouter, Query
from db.supabase_client import get_supabase
from typing import Optional
import os

router = APIRouter(prefix="/messages")

USER_ID = os.getenv("GHOST_USER_ID", "")

@router.get("/")
async def list_messages(
    contact: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
):
    sb = get_supabase()
    q = (
        sb.table("message_logs")
        .select("*")
        .eq("user_id", USER_ID)
        .order("created_at", desc=True)
        .limit(limit)
        .offset(offset)
    )
    if contact:
        q = q.eq("contact_phone", contact)
    r = q.execute()
    return {"messages": r.data or [], "count": len(r.data or [])}


@router.patch("/{message_id}/rating")
async def rate_message(message_id: str, rating: int):
    """rating: 1 = thumbs up, -1 = thumbs down"""
    if rating not in (1, -1):
        return {"error": "rating must be 1 or -1"}
    sb = get_supabase()
    sb.table("message_logs").update({"rating": rating}).eq("id", message_id).execute()
    return {"ok": True, "id": message_id, "rating": rating}


@router.get("/stats")
async def stats():
    sb = get_supabase()
    all_msgs = sb.table("message_logs").select("direction, ai_generated, rating").eq("user_id", USER_ID).execute()
    rows = all_msgs.data or []
    ai_replies = [r for r in rows if r["ai_generated"]]
    liked = [r for r in ai_replies if r.get("rating") == 1]
    disliked = [r for r in ai_replies if r.get("rating") == -1]
    return {
        "total_messages": len(rows),
        "ai_replies": len(ai_replies),
        "thumbs_up": len(liked),
        "thumbs_down": len(disliked),
        "satisfaction_rate": round(len(liked) / len(ai_replies) * 100) if ai_replies else 0,
    }
