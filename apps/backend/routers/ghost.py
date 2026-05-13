from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/ghost")

class GhostProfile(BaseModel):
    tone: str = "casual"                    # casual | formal | hinglish
    language: str = "english"               # english | tamil | hinglish | mixed
    sample_replies: List[str] = []          # up to 10 real past replies
    custom_instructions: Optional[str] = None
    active: bool = False

class GhostProfileResponse(GhostProfile):
    id: str
    user_id: str

@router.get("/profile")
async def get_profile():
    # TODO: fetch from Supabase for authenticated user
    return {"message": "Ghost profile endpoint — auth coming in next slice"}

@router.put("/profile")
async def update_profile(profile: GhostProfile):
    # TODO: upsert to Supabase
    return {"message": "Profile updated", "profile": profile}

@router.post("/toggle")
async def toggle(active: bool):
    # TODO: update ghost active state in Supabase + notify bridge
    return {"active": active}
