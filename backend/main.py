import subprocess
import time
import logging
from contextlib import asynccontextmanager
import httpx
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.database import engine, Base
from backend.db import models  # noqa: F401
from backend.api import quiz, recommendations, feedback, auth

logger = logging.getLogger("uvicorn.error")

Base.metadata.create_all(bind=engine)


def _ensure_ollama():
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        httpx.get(f"{ollama_url}/api/tags", timeout=2.0).raise_for_status()
        logger.info("Ollama already running.")
    except Exception:
        logger.info("Ollama not detected — starting 'ollama serve'...")
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Give it a moment to bind its port
        time.sleep(2)
        logger.info("Ollama started.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_ollama()
    yield


app = FastAPI(title="Podcast Recommender", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(quiz.router)
app.include_router(recommendations.router)
app.include_router(feedback.router)


@app.get("/health")
def health():
    return {"status": "ok"}
