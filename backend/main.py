from fastapi import FastAPI
from backend.db.database import engine, Base
from backend.db import models  # noqa: F401
from backend.api import quiz, recommendations, feedback

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Podcast Recommender")
app.include_router(quiz.router)
app.include_router(recommendations.router)
app.include_router(feedback.router)


@app.get("/health")
def health():
    return {"status": "ok"}
