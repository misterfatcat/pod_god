import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.database import engine, Base
from backend.db import models  # noqa


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_submit_feedback_returns_200():
    payload = {
        "episode_id": 999,
        "reaction": "like",
        "completion_pct": 85,
        "did_finish": False,
        "listen_context": "commute",
        "great_storytelling": True,
        "too_long": False,
        "poor_audio": False,
        "fascinating_topic": True,
        "too_basic": False,
        "too_advanced": False,
        "loved_guest": False,
        "repetitive": False,
        "great_production": False,
        "too_short": False,
        "reason_text": "Really engaging narrative"
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["reaction"] == "like"
    assert data["great_storytelling"] is True


def test_feedback_requires_reaction():
    response = client.post("/feedback", json={"episode_id": 1})
    assert response.status_code == 422
