from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.database import engine, Base
from backend.db import models  # noqa: F401
from backend.api import quiz, recommendations, feedback, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Podcast Recommender")

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
