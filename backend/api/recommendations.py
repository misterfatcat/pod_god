import json
import logging
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx
from backend.db.database import get_db
from backend.db.models import UserProfile, Episode, Recommendation, Feedback, User
from backend.services.podcast_index import PodcastIndexClient
from backend.services.recommender import score_episodes, apply_feedback_weights
from backend.services.ollama import OllamaClient
from backend.services.auth import get_current_user

router = APIRouter()
logger = logging.getLogger("uvicorn.error")
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _get_week_start() -> str:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat()


async def _generate_for_user(user_id: int, db: Session) -> dict:
    """Core generation logic, usable by both the HTTP endpoint and the scheduler."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise ValueError("Complete the quiz first.")

    profile_dict = {
        "interest_categories": json.loads(profile.interest_categories),
        "goals": json.loads(profile.goals),
        "preferred_formats": json.loads(profile.preferred_formats),
        "preferred_length_bucket": profile.preferred_length_bucket,
        "complexity_level": profile.complexity_level,
        "trending_vs_timeless": profile.trending_vs_timeless,
        "mainstream_vs_niche": profile.mainstream_vs_niche,
    }

    # Fetch candidates from Podcast Index
    pi_client = PodcastIndexClient()
    categories = [c["category"] for c in profile_dict["interest_categories"]]
    raw_episodes = await pi_client.search_episodes(categories, limit=30)

    scored = score_episodes(raw_episodes, profile_dict)

    # Apply feedback weights scoped to current user
    recent_feedback = (
        db.query(Feedback)
        .filter(Feedback.user_id == user_id)
        .order_by(Feedback.created_at.desc())
        .limit(20)
        .all()
    )
    feedback_history = []
    for fb in recent_feedback:
        ep = fb.episode
        feedback_history.append({
            "categories": json.loads(ep.categories) if ep else [],
            "reaction": fb.reaction,
            "great_storytelling": fb.great_storytelling,
            "fascinating_topic": fb.fascinating_topic,
            "repetitive": fb.repetitive,
            "too_long": fb.too_long,
            "too_basic": fb.too_basic,
            "too_advanced": fb.too_advanced,
        })
    if feedback_history:
        scored = apply_feedback_weights(scored, feedback_history)

    top_candidates = scored[:15]

    # Build feedback summary for the LLM prompt
    feedback_summary = "; ".join(
        f"{'Liked' if fb.reaction == 'like' else 'Disliked'}: episode {fb.episode_id}"
        for fb in recent_feedback
    ) or "None yet"

    # LLM ranking
    ollama = OllamaClient()
    ranked = ollama.rank_episodes(top_candidates, profile_dict, feedback_summary)

    # Store episodes and recommendations scoped to current user
    week_of = _get_week_start()
    db.query(Recommendation).filter(
        Recommendation.week_of == week_of,
        Recommendation.user_id == user_id,
    ).delete()

    episodes_per_day = 3
    result = {}
    for day_idx, day in enumerate(DAYS):
        day_eps = ranked[day_idx * episodes_per_day: (day_idx + 1) * episodes_per_day]
        result[day] = []
        for rank, ep_data in enumerate(day_eps, start=1):
            episode = db.query(Episode).filter(
                Episode.podcast_index_id == ep_data["podcast_index_id"]
            ).first()
            if not episode:
                episode = Episode(**{
                    k: v for k, v in ep_data.items()
                    if k not in ("score", "matched_criteria", "reason")
                    and hasattr(Episode, k)
                })
                db.add(episode)
                db.flush()

            rec = Recommendation(
                week_of=week_of,
                day_of_week=day,
                rank=rank,
                episode_id=episode.id,
                score=ep_data.get("score", 0.0),
                matched_criteria=json.dumps(ep_data.get("matched_criteria", [])),
                llm_reason=ep_data.get("reason", ""),
                llm_model_version=ollama.model,
                user_id=user_id,
            )
            db.add(rec)
            result[day].append({
                "rank": rank,
                "title": ep_data["title"],
                "reason": ep_data.get("reason", ""),
            })

    db.commit()
    return {"week_of": week_of, "recommendations": result}


@router.post("/recommendations/generate")
async def generate_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await _generate_for_user(current_user.id, db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Podcast Index API credentials are not configured. "
                    "Sign up free at https://api.podcastindex.org, then add "
                    "PODCAST_INDEX_API_KEY and PODCAST_INDEX_API_SECRET to your .env file."
                ),
            )
        raise HTTPException(status_code=503, detail=f"Podcast Index API error: {exc.response.status_code}")


@router.get("/recommendations/week")
def get_week_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    week_of = _get_week_start()
    recs = db.query(Recommendation).filter(
        Recommendation.week_of == week_of,
        Recommendation.user_id == current_user.id,
    ).all()
    if not recs:
        raise HTTPException(
            status_code=404,
            detail="No recommendations yet. POST /recommendations/generate first.",
        )
    result = {day: [] for day in DAYS}
    for rec in sorted(recs, key=lambda r: (r.day_of_week, r.rank)):
        ep = rec.episode
        result[rec.day_of_week].append({
            "rank": rec.rank,
            "id": rec.id,
            "episode_id": rec.episode_id,
            "title": ep.title if ep else "",
            "artwork_url": ep.artwork_url if ep else "",
            "duration_sec": ep.duration_sec if ep else 0,
            "audio_url": ep.audio_url if ep else "",
            "reason": rec.llm_reason,
            "was_listened": rec.was_listened,
            "description": ep.description if ep else "",
            "published_at": ep.published_at.isoformat() if ep and ep.published_at else None,
            "host_name": ep.host_name if ep else None,
        })
    return {"week_of": week_of, "recommendations": result}
