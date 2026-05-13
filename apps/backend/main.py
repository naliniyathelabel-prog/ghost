from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers.webhook import router as webhook_router
from routers.ghost import router as ghost_router

app = FastAPI(title="Ghost API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(ghost_router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "ghost-backend"}

@app.get("/")
def root():
    return {"message": "Ghost API — https://github.com/naliniyathelabel-prog/ghost"}
