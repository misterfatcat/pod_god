LENGTH_RANGES = {
    "under_20": (0, 1200),
    "20_to_45": (1200, 2700),
    "over_45": (2700, float("inf")),
    "no_preference": (0, float("inf")),
}


def score_episodes(episodes: list[dict], profile: dict) -> list[dict]:
    scored = []
    for ep in episodes:
        score = 0.0
        matched = []

        # Length match (0.3 weight)
        pref = profile.get("preferred_length_bucket", "no_preference")
        lo, hi = LENGTH_RANGES.get(pref, (0, float("inf")))
        dur = ep.get("duration_sec", 0)
        if lo <= dur <= hi:
            score += 0.3
            matched.append("length")

        # Category match (0.4 weight, scaled by intensity)
        interest_cats = {c["category"].lower() for c in profile.get("interest_categories", [])}
        ep_cats = {c.lower() for c in ep.get("categories", [])}
        overlap = interest_cats & ep_cats
        if overlap:
            intensities = [
                c["intensity"] for c in profile.get("interest_categories", [])
                if c["category"].lower() in overlap
            ]
            score += 0.4 * (sum(intensities) / (5 * max(len(intensities), 1)))
            matched.append("category")

        # Format match (0.15 weight)
        pref_formats = profile.get("preferred_formats", [])
        if not pref_formats or ep.get("content_format") in pref_formats:
            score += 0.15
            matched.append("format")

        # Complexity match (0.15 weight)
        if ep.get("complexity_level") == profile.get("complexity_level"):
            score += 0.15
            matched.append("complexity")

        scored.append({**ep, "score": round(score, 3), "matched_criteria": matched})

    return sorted(scored, key=lambda e: e["score"], reverse=True)


def apply_feedback_weights(scored: list[dict], feedback_history: list[dict]) -> list[dict]:
    for ep in scored:
        ep_cats = {c.lower() for c in ep.get("categories", [])}
        boost = 0.0
        for fb in feedback_history:
            fb_cats = {c.lower() for c in fb.get("categories", [])}
            overlap = ep_cats & fb_cats
            if not overlap:
                continue
            if fb.get("reaction") == "like":
                boost += 0.1
                if fb.get("great_storytelling"):
                    boost += 0.05
                if fb.get("fascinating_topic"):
                    boost += 0.05
            elif fb.get("reaction") == "dislike":
                boost -= 0.1
                if fb.get("repetitive"):
                    boost -= 0.05
                if fb.get("too_long") and ep.get("duration_sec", 0) > 2700:
                    boost -= 0.05
            elif fb.get("reaction") == "not_interested":
                boost -= 0.1
                if fb.get("too_basic"):
                    boost -= 0.05
                if fb.get("too_advanced"):
                    boost -= 0.05
                if fb.get("too_long") and ep.get("duration_sec", 0) > 2700:
                    boost -= 0.05
        ep["score"] = round(max(0.0, min(1.0, ep["score"] + boost)), 3)
    return sorted(scored, key=lambda e: e["score"], reverse=True)
