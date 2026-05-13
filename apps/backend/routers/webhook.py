from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx, os

router = APIRouter(prefix="/webhook")

BRIDGE_SECRET = os.getenv("BRIDGE_SECRET", "change-me")

class InboundMessage(BaseModel):
    from_: str
    text: str
    timestamp: int

    class Config:
        populate_by_name = True
        fields = {"from_": "from"}

@router.post("/inbound")
async def inbound(msg: InboundMessage, x_bridge_secret: Optional[str] = Header(None)):
    if x_bridge_secret != BRIDGE_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # TODO: fetch ghost_profile from Supabase
    # TODO: fetch last 10 messages from this contact
    # TODO: call AI to generate reply
    # TODO: POST /send to bridge
    # TODO: log message to Supabase

    return {"received": True, "from": msg.from_, "text": msg.text}
