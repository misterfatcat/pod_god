from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.db.database import Base


class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional demographics
    age_range = Column(String, nullable=True)
    location_region = Column(String, nullable=True)

    # Stored as JSON strings
    interest_categories = Column(Text, default="[]")
    goals = Column(Text, default="{}")
    preferred_formats = Column(Text, default="[]")
    preferred_listen_schedule = Column(Text, default="{}")

    preferred_length_bucket = Column(String, default="no_preference")
    complexity_level = Column(String, default="balanced")
    trending_vs_timeless = Column(String, default="mixed")
    mainstream_vs_niche = Column(String, default="no_preference")


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    podcast_index_id = Column(String, unique=True, index=True)
    podcast_id = Column(String, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    title = Column(String)
    description = Column(Text)
    duration_sec = Column(Integer)
    published_at = Column(DateTime, nullable=True)
    audio_url = Column(String)
    artwork_url = Column(String)

    # Stored as JSON strings
    categories = Column(Text, default="[]")
    topic_tags = Column(Text, default="[]")
    guest_names = Column(Text, default="[]")

    content_format = Column(String, nullable=True)
    complexity_level = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    host_name = Column(String, nullable=True)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    week_of = Column(String, index=True)
    day_of_week = Column(String)
    rank = Column(Integer)

    episode_id = Column(Integer, ForeignKey("episodes.id"))
    episode = relationship("Episode")

    score = Column(Float, default=0.0)
    matched_criteria = Column(Text, default="[]")
    llm_reason = Column(Text, nullable=True)
    llm_model_version = Column(String, nullable=True)
    was_listened = Column(Boolean, default=False)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    episode_id = Column(Integer, ForeignKey("episodes.id"))
    episode = relationship("Episode")

    reaction = Column(String)
    completion_pct = Column(Integer, default=0)
    did_finish = Column(Boolean, default=False)
    listen_context = Column(String, nullable=True)

    too_long = Column(Boolean, default=False)
    too_short = Column(Boolean, default=False)
    great_storytelling = Column(Boolean, default=False)
    poor_audio = Column(Boolean, default=False)
    fascinating_topic = Column(Boolean, default=False)
    too_basic = Column(Boolean, default=False)
    too_advanced = Column(Boolean, default=False)
    loved_guest = Column(Boolean, default=False)
    repetitive = Column(Boolean, default=False)
    great_production = Column(Boolean, default=False)

    reason_text = Column(Text, nullable=True)
