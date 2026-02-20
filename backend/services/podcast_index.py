import hashlib
import time
import os
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class PodcastIndexClient:
    BASE_URL = "https://api.podcastindex.org/api/1.0"

    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or os.getenv("PODCAST_INDEX_API_KEY")
        self.api_secret = api_secret or os.getenv("PODCAST_INDEX_API_SECRET")

    def _auth_headers(self) -> dict:
        epoch = int(time.time())
        hash_input = f"{self.api_key}{self.api_secret}{epoch}"
        auth_hash = hashlib.sha1(hash_input.encode()).hexdigest()
        return {
            "X-Auth-Key": self.api_key,
            "X-Auth-Date": str(epoch),
            "Authorization": auth_hash,
            "User-Agent": "PodcastRecommender/1.0",
        }

    async def search_episodes(self, categories: list[str], limit: int = 20) -> list[dict]:
        query = " ".join(categories[:3])
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/search/byterm",
                params={"q": query, "max": limit, "fulltext": True},
                headers=self._auth_headers(),
            )
            resp.raise_for_status()
            data = resp.json()

        return [self._normalize(item) for item in data.get("items", [])]

    def _normalize(self, item: dict) -> dict:
        published = item.get("datePublished")
        return {
            "podcast_index_id": str(item.get("id", "")),
            "podcast_id": str(item.get("feedId", "")),
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "duration_sec": item.get("duration", 0),
            "published_at": datetime.utcfromtimestamp(published).isoformat() if published else None,
            "audio_url": item.get("enclosureUrl", ""),
            "artwork_url": item.get("feedImage", ""),
            "categories": list(item.get("categories", {}).values()),
            "topic_tags": [],
            "guest_names": [],
            "host_name": None,
            "content_format": None,
            "sentiment": None,
            "complexity_level": None,
        }
