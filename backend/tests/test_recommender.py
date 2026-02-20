from backend.services.recommender import score_episodes, apply_feedback_weights

PROFILE = {
    "interest_categories": [{"category": "technology", "intensity": 5}],
    "preferred_length_bucket": "20_to_45",
    "complexity_level": "balanced",
    "trending_vs_timeless": "mixed",
    "mainstream_vs_niche": "no_preference",
    "preferred_formats": ["interview"],
}


def make_episode(**kwargs):
    base = {
        "podcast_index_id": "1",
        "title": "Test",
        "duration_sec": 1800,
        "categories": ["Technology"],
        "complexity_level": "balanced",
        "content_format": "interview",
        "published_at": "2024-01-01T00:00:00",
    }
    return {**base, **kwargs}


def test_episode_matching_all_criteria_scores_high():
    episodes = [make_episode()]
    scored = score_episodes(episodes, PROFILE)
    assert scored[0]["score"] > 0.5


def test_too_short_episode_scores_lower():
    short = make_episode(duration_sec=600)   # 10 min — outside 20-45 pref
    normal = make_episode(duration_sec=1800) # 30 min — matches
    scored = score_episodes([short, normal], PROFILE)
    scores = {e["duration_sec"]: e["score"] for e in scored}
    assert scores[1800] > scores[600]


def test_returns_sorted_by_score_descending():
    episodes = [make_episode(duration_sec=600), make_episode(duration_sec=1800)]
    scored = score_episodes(episodes, PROFILE)
    assert scored[0]["score"] >= scored[1]["score"]


def test_matched_criteria_populated():
    episodes = [make_episode()]
    scored = score_episodes(episodes, PROFILE)
    assert len(scored[0]["matched_criteria"]) > 0


def test_liked_categories_boost_score():
    tech_ep = make_episode(categories=["Technology"])
    history_ep = make_episode(podcast_index_id="2", categories=["History"])
    feedback_history = [{"categories": ["Technology"], "reaction": "like", "great_storytelling": True}]
    scored = score_episodes([tech_ep, history_ep], PROFILE)
    weighted = apply_feedback_weights(scored, feedback_history)
    tech_score = next(e["score"] for e in weighted if "Technology" in e["categories"])
    history_score = next(e["score"] for e in weighted if "History" in e["categories"])
    assert tech_score > history_score


def test_disliked_categories_reduce_score():
    episodes = [make_episode()]
    feedback_history = [{"categories": ["Technology"], "reaction": "dislike", "repetitive": True}]
    scored = score_episodes(episodes, PROFILE)
    baseline = scored[0]["score"]
    weighted = apply_feedback_weights(scored, feedback_history)
    assert weighted[0]["score"] <= baseline


def test_feedback_weights_score_stays_within_bounds():
    episodes = [make_episode()]
    # Many positive signals shouldn't push score above 1.0
    feedback_history = [
        {"categories": ["Technology"], "reaction": "like", "great_storytelling": True, "fascinating_topic": True}
        for _ in range(20)
    ]
    scored = score_episodes(episodes, PROFILE)
    weighted = apply_feedback_weights(scored, feedback_history)
    assert weighted[0]["score"] <= 1.0
    assert weighted[0]["score"] >= 0.0
