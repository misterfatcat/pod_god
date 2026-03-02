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

    async def _fetch_feeds_for_query(
        self, client: httpx.AsyncClient, query: str, max_feeds: int = 8
    ) -> list[dict]:
        resp = await client.get(
            f"{self.BASE_URL}/search/byterm",
            params={"q": query, "max": max_feeds},
            headers=self._auth_headers(),
        )
        resp.raise_for_status()
        return resp.json().get("feeds", [])

    async def search_episodes(self, categories: list[str], limit: int = 20) -> list[dict]:
        async with httpx.AsyncClient() as client:
            # Search each category separately so we get diverse results
            all_feeds: dict[int, dict] = {}
            for cat in categories[:5]:
                for feed in await self._fetch_feeds_for_query(client, cat):
                    all_feeds[feed["id"]] = feed

            # Fetch recent episodes from each unique feed
            raw_episodes: list[dict] = []
            for feed in list(all_feeds.values())[:20]:
                feed_id = feed.get("id")
                feed_categories = list(feed.get("categories", {}).values())
                feed_image = feed.get("image") or feed.get("artwork") or ""
                ep_resp = await client.get(
                    f"{self.BASE_URL}/episodes/byfeedid",
                    params={"id": feed_id, "max": 4},
                    headers=self._auth_headers(),
                )
                if ep_resp.status_code == 200:
                    for item in ep_resp.json().get("items", []):
                        item["_feed_categories"] = feed_categories
                        item["_feed_image"] = feed_image
                        raw_episodes.append(item)

        # Deduplicate by episode id
        seen: set[str] = set()
        unique: list[dict] = []
        for ep in raw_episodes:
            eid = str(ep.get("id", ""))
            if eid and eid not in seen:
                seen.add(eid)
                unique.append(ep)

        return [self._normalize(ep) for ep in unique[:limit]]

    def _normalize(self, item: dict) -> dict:
        published = item.get("datePublished")
        # Use episode image first, then feed image, then feedImage field
        artwork = item.get("image") or item.get("_feed_image") or item.get("feedImage") or ""
        # Use feed categories since individual episodes rarely have their own
        cats = item.get("_feed_categories") or list(item.get("categories", {}).values())
        return {
            "podcast_index_id": str(item.get("id", "")),
            "podcast_id": str(item.get("feedId", "")),
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "duration_sec": item.get("duration", 0),
            "published_at": datetime.utcfromtimestamp(published) if published else None,
            "audio_url": item.get("enclosureUrl", ""),
            "artwork_url": artwork,
            "categories": cats,
            "topic_tags": [],
            "guest_names": [],
            "host_name": None,
            "content_format": None,
            "sentiment": None,
            "complexity_level": None,
        }
