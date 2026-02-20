from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import Feedback, User
from backend.services.auth import get_current_user

router = APIRouter()


class FeedbackSubmission(BaseModel):
    episode_id: int
    reaction: str  # like|dislike|skip|neutral
    completion_pct: int = 0
    did_finish: bool = False
    listen_context: Optional[str] = None
    too_long: bool = False
    too_short: bool = False
    great_storytelling: bool = False
    poor_audio: bool = False
    fascinating_topic: bool = False
    too_basic: bool = False
    too_advanced: bool = False
    loved_guest: bool = False
    repetitive: bool = False
    great_production: bool = False
    reason_text: Optional[str] = None


@router.post("/feedback")
def submit_feedback(
    submission: FeedbackSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    feedback = Feedback(**submission.model_dump(), user_id=current_user.id)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return {
        "id": feedback.id,
        "reaction": feedback.reaction,
        "great_storytelling": feedback.great_storytelling,
        "fascinating_topic": feedback.fascinating_topic,
    }
