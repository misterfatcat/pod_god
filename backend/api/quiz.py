import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import UserProfile

router = APIRouter()


class InterestCategory(BaseModel):
    category: str
    intensity: int  # 1-5


class Goals(BaseModel):
    primary: str
    secondary: list[str] = []


class QuizSubmission(BaseModel):
    interest_categories: list[InterestCategory]
    goals: Goals
    preferred_formats: list[str]
    preferred_length_bucket: str
    complexity_level: str
    trending_vs_timeless: str
    mainstream_vs_niche: str
    preferred_listen_schedule: dict
    age_range: Optional[str] = None
    location_region: Optional[str] = None


def _profile_to_dict(profile: UserProfile) -> dict:
    return {
        "id": profile.id,
        "interest_categories": json.loads(profile.interest_categories),
        "goals": json.loads(profile.goals),
        "preferred_formats": json.loads(profile.preferred_formats),
        "preferred_length_bucket": profile.preferred_length_bucket,
        "complexity_level": profile.complexity_level,
        "trending_vs_timeless": profile.trending_vs_timeless,
        "mainstream_vs_niche": profile.mainstream_vs_niche,
        "preferred_listen_schedule": json.loads(profile.preferred_listen_schedule),
        "age_range": profile.age_range,
        "location_region": profile.location_region,
    }


@router.post("/quiz")
def submit_quiz(submission: QuizSubmission, db: Session = Depends(get_db)):
    # Replace existing profile (single-user local app)
    db.query(UserProfile).delete()
    profile = UserProfile(
        interest_categories=json.dumps([c.model_dump() for c in submission.interest_categories]),
        goals=json.dumps(submission.goals.model_dump()),
        preferred_formats=json.dumps(submission.preferred_formats),
        preferred_length_bucket=submission.preferred_length_bucket,
        complexity_level=submission.complexity_level,
        trending_vs_timeless=submission.trending_vs_timeless,
        mainstream_vs_niche=submission.mainstream_vs_niche,
        preferred_listen_schedule=json.dumps(submission.preferred_listen_schedule),
        age_range=submission.age_range,
        location_region=submission.location_region,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _profile_to_dict(profile)


@router.get("/profile")
def get_profile(db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found. Complete the quiz first.")
    return _profile_to_dict(profile)
