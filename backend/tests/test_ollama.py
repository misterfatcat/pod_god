import pytest
from unittest.mock import patch, MagicMock
from backend.services.ollama import OllamaClient


@pytest.fixture
def client():
    return OllamaClient(base_url="http://localhost:11434", model="llama3.2")


def test_rank_episodes_returns_ordered_list(client):
    candidates = [
        {"podcast_index_id": "1", "title": "AI Today", "description": "LLMs explained", "score": 0.8},
        {"podcast_index_id": "2", "title": "History Hour", "description": "Ancient Rome", "score": 0.5},
    ]
    profile = {
        "goals": {"primary": "learn"},
        "interest_categories": [{"category": "technology", "intensity": 5}],
        "complexity_level": "balanced",
    }
    feedback_summary = "Liked: 'AI Today' (great storytelling). Disliked: 'History Hour' (too long)."

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": '{"rankings": [{"id": "1", "reason": "Matches your AI interest"}, {"id": "2", "reason": "History but you prefer tech"}]}'
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.post", return_value=mock_response):
        result = client.rank_episodes(candidates, profile, feedback_summary)

    assert len(result) == 2
    assert result[0]["podcast_index_id"] == "1"
    assert "reason" in result[0]


def test_rank_episodes_falls_back_on_bad_json(client):
    candidates = [
        {"podcast_index_id": "1", "title": "AI Today", "description": "LLMs explained", "score": 0.8},
    ]
    profile = {"goals": {"primary": "learn"}, "interest_categories": [], "complexity_level": "balanced"}

    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Sorry, I cannot help with that."}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.post", return_value=mock_response):
        result = client.rank_episodes(candidates, profile)

    assert len(result) == 1
    assert result[0]["podcast_index_id"] == "1"
    assert "reason" in result[0]
