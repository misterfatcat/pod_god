import json
import httpx
import os
from dotenv import load_dotenv

load_dotenv()


class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")

    def rank_episodes(
        self,
        candidates: list[dict],
        profile: dict,
        feedback_summary: str = "",
    ) -> list[dict]:
        candidate_text = "\n".join(
            f"ID: {ep['podcast_index_id']} | Title: {ep['title']} | {ep.get('description', '')[:200]}"
            for ep in candidates[:10]
        )
        prompt = f"""You are a podcast recommendation engine. Rank these episodes for this listener.

Listener profile:
- Primary goal: {profile.get('goals', {}).get('primary', 'learn')}
- Interests: {', '.join(c['category'] for c in profile.get('interest_categories', []))}
- Complexity preference: {profile.get('complexity_level', 'balanced')}

Recent feedback: {feedback_summary or 'None yet'}

Episodes to rank:
{candidate_text}

Return ONLY valid JSON like:
{{"rankings": [{{"id": "episode_id", "reason": "why it fits this listener"}}]}}

Rank from best to worst fit. Include all episodes."""

        try:
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
                timeout=60.0,
            )
            response.raise_for_status()
            raw = response.json().get("response", "{}")
        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError, httpx.RemoteProtocolError):
            # Ollama not running, overloaded, or model unavailable — fall back to rule-based score order
            return [{**ep, "reason": "Recommended based on your interests"} for ep in candidates]

        try:
            parsed = json.loads(raw)
            rankings = parsed.get("rankings", [])
        except json.JSONDecodeError:
            return [{**ep, "reason": "Recommended based on your interests"} for ep in candidates]

        id_to_ep = {ep["podcast_index_id"]: ep for ep in candidates}
        result = []
        for rank in rankings:
            ep_id = str(rank.get("id", ""))
            if ep_id in id_to_ep:
                result.append({**id_to_ep[ep_id], "reason": rank.get("reason", "")})

        # Include any candidates the LLM omitted (append at end)
        ranked_ids = {str(r.get("id", "")) for r in rankings}
        for ep in candidates:
            if ep["podcast_index_id"] not in ranked_ids:
                result.append({**ep, "reason": "Recommended based on your interests"})

        return result
