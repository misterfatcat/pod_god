import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.database import engine, Base, SessionLocal
from backend.db import models  # noqa
from backend.db.models import User
from backend.services.auth import get_current_user


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    test_user = User(email="test@test.com", hashed_password="x")
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    app.dependency_overrides[get_current_user] = lambda: test_user
    db.close()
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_submit_quiz_returns_200():
    payload = {
        "interest_categories": [{"category": "technology", "intensity": 4}],
        "goals": {"primary": "learn", "secondary": ["professional"]},
        "preferred_formats": ["interview", "solo"],
        "preferred_length_bucket": "20_to_45",
        "complexity_level": "balanced",
        "trending_vs_timeless": "mixed",
        "mainstream_vs_niche": "no_preference",
        "preferred_listen_schedule": {"monday": ["morning"], "wednesday": ["evening"]},
        "age_range": "25-34",
        "location_region": "US-West"
    }
    response = client.post("/quiz", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["complexity_level"] == "balanced"


def test_get_profile_returns_saved_data():
    payload = {
        "interest_categories": [{"category": "science", "intensity": 5}],
        "goals": {"primary": "learn", "secondary": []},
        "preferred_formats": ["narrative"],
        "preferred_length_bucket": "over_45",
        "complexity_level": "deep_dive",
        "trending_vs_timeless": "timeless",
        "mainstream_vs_niche": "niche",
        "preferred_listen_schedule": {},
    }
    client.post("/quiz", json=payload)
    response = client.get("/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["complexity_level"] == "deep_dive"
    assert data["trending_vs_timeless"] == "timeless"


def test_submit_quiz_replaces_existing_profile():
    payload_1 = {
        "interest_categories": [], "goals": {"primary": "learn", "secondary": []},
        "preferred_formats": [], "preferred_length_bucket": "under_20",
        "complexity_level": "beginner", "trending_vs_timeless": "trending",
        "mainstream_vs_niche": "mainstream", "preferred_listen_schedule": {}
    }
    payload_2 = {**payload_1, "complexity_level": "deep_dive"}
    client.post("/quiz", json=payload_1)
    client.post("/quiz", json=payload_2)
    response = client.get("/profile")
    assert response.json()["complexity_level"] == "deep_dive"
