import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.database import engine, Base, SessionLocal
from backend.db import models  # noqa
from backend.db.models import User, UserProfile
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


@pytest.fixture
def user_with_profile():
    """Create a user profile so the regenerate endpoint can proceed."""
    db = SessionLocal()
    profile = UserProfile(
        user_id=1,
        interest_categories=json.dumps([{"category": "technology", "intensity": 4}]),
        goals=json.dumps({"primary": "learn", "secondary": []}),
        preferred_formats=json.dumps(["interview"]),
        preferred_length_bucket="20_to_45",
        complexity_level="balanced",
        trending_vs_timeless="mixed",
        mainstream_vs_niche="no_preference",
    )
    db.add(profile)
    db.commit()
    db.close()


# Minimal episode dicts that satisfy the Episode model fields accessed in the endpoint
def _make_episode(n: int) -> dict:
    return {
        "podcast_index_id": f"pi_{n}",
        "title": f"Episode {n}",
        "description": "A test episode",
        "audio_url": f"https://example.com/{n}.mp3",
        "artwork_url": "",
        "duration_sec": 1800,
        "published_at": None,
        "host_name": None,
        "categories": ["technology"],
        "topic_tags": [],
        "guest_names": [],
        "score": 0.9 - n * 0.1,
        "matched_criteria": [],
        "reason": f"Reason {n}",
    }


client = TestClient(app)


def test_regenerate_day_invalid_day_returns_400():
    response = client.post("/recommendations/regenerate/funday")
    assert response.status_code == 400
    assert "Invalid day" in response.json()["detail"]


def test_regenerate_day_returns_3_episodes(user_with_profile):
    raw_episodes = [_make_episode(i) for i in range(10)]
    ranked_episodes = [_make_episode(i) for i in range(3)]

    mock_pi = AsyncMock()
    mock_pi.search_episodes = AsyncMock(return_value=raw_episodes)

    mock_ollama = MagicMock()
    mock_ollama.model = "llama3"
    mock_ollama.rank_episodes = MagicMock(return_value=ranked_episodes)

    with (
        patch("backend.api.recommendations.PodcastIndexClient", return_value=mock_pi),
        patch("backend.api.recommendations.OllamaClient", return_value=mock_ollama),
        patch("backend.api.recommendations.score_episodes", return_value=raw_episodes),
        patch("backend.api.recommendations.apply_feedback_weights", return_value=raw_episodes),
    ):
        response = client.post("/recommendations/regenerate/monday")

    assert response.status_code == 200
    data = response.json()
    assert data["day"] == "monday"
    assert "monday" in data["recommendations"]
    assert len(data["recommendations"]["monday"]) == 3
    first = data["recommendations"]["monday"][0]
    assert first["rank"] == 1
    assert "title" in first
    assert "reason" in first
    # Full episode shape required by EpisodeCard and FeedbackModal
    assert "id" in first
    assert "episode_id" in first
    assert "artwork_url" in first
    assert "duration_sec" in first
    assert "audio_url" in first
    assert "categories" in first
    assert "was_listened" in first
