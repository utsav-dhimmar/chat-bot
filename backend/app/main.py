"""
backend/main.py
---------------
FastAPI application entry point.

Registers all routers, CORS middleware, and startup events.

Run with:
    uv run uvicorn backend.main:app --reload --port 8000

API docs at:
    http://localhost:8000/docs
"""

# Load .env FIRST before any other imports read env vars
import os

try:
    from dotenv import load_dotenv

    load_dotenv(override=True)
    print(f"[Env] DATABASE_URL = {os.getenv('DATABASE_URL', 'NOT FOUND')[:50]}")
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, chat, documents
from app.db.session import create_all_tables
from app.services.dspy_module import init_dspy

app = FastAPI(
    title="File-Based Chatbot API",
    description="Answers questions only from uploaded documents — no hallucination.",
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Allow the React frontend (Dev 3) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    # Create DB tables (dev only — use Alembic in production)
    await create_all_tables()
    # Initialise DSPy + HuggingFace backend
    init_dspy()
    print("[App] Startup complete — ready to serve requests")


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(documents.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
