import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from backend.services.podcast_index import PodcastIndexClient


@pytest.fixture
def client():
    return PodcastIndexClient(api_key="test_key", api_secret="test_secret")


async def test_search_returns_episodes(client):
    # First call: /search/byterm expects {"feeds": [...]}
    feed_resp = MagicMock()
    feed_resp.raise_for_status = MagicMock()
    feed_resp.json.return_value = {
        "feeds": [{"id": 1, "image": "http://example.com/art.jpg", "categories": {"1": "Technology"}}]
    }

    # Second call: /episodes/byfeedid expects {"items": [...]}
    episode_resp = MagicMock()
    episode_resp.status_code = 200
    episode_resp.json.return_value = {
        "items": [
            {
                "id": "abc123",
                "feedId": 1,
                "title": "Test Episode",
                "description": "Great ep",
                "duration": 1800,
                "datePublished": 1700000000,
                "enclosureUrl": "http://example.com/ep.mp3",
                "feedImage": "http://example.com/art.jpg",
            }
        ]
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [feed_resp, episode_resp]
        episodes = await client.search_episodes(["technology"], limit=5)

    assert len(episodes) == 1
    assert episodes[0]["title"] == "Test Episode"
    assert episodes[0]["duration_sec"] == 1800


async def test_search_handles_empty_results(client):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"items": []}
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        episodes = await client.search_episodes(["nonexistenttopic99"], limit=5)

    assert episodes == []
