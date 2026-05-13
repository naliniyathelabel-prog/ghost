from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import webhook, ghost

app = FastAPI(title="Ghost API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)
app.include_router(ghost.router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "ghost-backend"}

@app.get("/")
def root():
    return {"message": "Ghost API — Life is short, automate things."}
