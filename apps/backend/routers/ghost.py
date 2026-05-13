from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os

from db import get_supabase

router = APIRouter(prefix="/ghost")

# MVP: single-user mode — user_id from env
def _user_id() -> str:
    uid = os.getenv("GHOST_USER_ID", "")
    if not uid:
        raise HTTPException(status_code=500, detail="GHOST_USER_ID not configured")
    return uid


class GhostProfile(BaseModel):
    name: Optional[str] = None
    tone: str = "casual"
    language: str = "english"
    description: Optional[str] = None
    sample_replies: List[str] = []
    custom_instructions: Optional[str] = None
    active: bool = False
    tier: str = "free"


@router.get("/profile")
def get_profile():
    db = get_supabase()
    r = db.table("ghost_profiles").select("*").eq("user_id", _user_id()).single().execute()
    if not r.data:
        raise HTTPException(status_code=404, detail="Ghost profile not found — create one first")
    return r.data


@router.put("/profile")
def update_profile(profile: GhostProfile):
    db = get_supabase()
    data = profile.model_dump()
    data["user_id"] = _user_id()
    r = db.table("ghost_profiles").upsert(data, on_conflict="user_id").execute()
    return {"ok": True, "profile": r.data[0] if r.data else data}


@router.post("/toggle")
def toggle(active: bool):
    db = get_supabase()
    r = (
        db.table("ghost_profiles")
        .update({"active": active})
        .eq("user_id", _user_id())
        .execute()
    )
    return {"active": active, "updated": bool(r.data)}


@router.get("/messages")
def get_messages(contact: Optional[str] = None, limit: int = 50):
    db = get_supabase()
    q = (
        db.table("message_logs")
        .select("*")
        .eq("user_id", _user_id())
        .order("created_at", desc=True)
        .limit(limit)
    )
    if contact:
        q = q.eq("contact_phone", contact)
    r = q.execute()
    return {"messages": r.data or []}


@router.post("/messages/{message_id}/rate")
def rate_message(message_id: str, rating: int):
    if rating not in (1, -1):
        raise HTTPException(status_code=400, detail="Rating must be 1 or -1")
    db = get_supabase()
    r = (
        db.table("message_logs")
        .update({"rating": rating})
        .eq("id", message_id)
        .eq("user_id", _user_id())
        .execute()
    )
    return {"ok": True, "message_id": message_id, "rating": rating}
