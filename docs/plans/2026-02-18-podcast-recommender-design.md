# Podcast Recommender — Design Doc
**Date:** 2026-02-18
**Status:** Approved

---

## Problem

Discovering what to listen to each week is overwhelming. There's no tool that combines your interests, goals, schedule, and evolving taste (likes/dislikes with reasons) to surface genuinely relevant podcast episodes — and gets smarter over time.

## Outcome

A local web app that generates a weekly list of 3 podcast episode recommendations per day, personalized via an onboarding quiz and refined over time through structured feedback. Built feature-by-feature with tests at each phase. Designed to be ML-ready from day one.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLite (SQLAlchemy) |
| Package management | `uv` (`pyproject.toml`) |
| Frontend | React + Vite |
| Podcast data | Podcast Index API (free, open) |
| LLM | Ollama (local) — moderately-sized model (e.g. llama3.2) |
| Testing | pytest (backend), Vitest (frontend) |

---

## Project Structure

```
podcast_sort/
├── pyproject.toml           # uv-managed Python deps
├── .env                     # API keys, Ollama config (gitignored)
├── .env.example             # committed template
├── Makefile                 # dev, test, install shortcuts
├── backend/
│   ├── main.py              # FastAPI app entrypoint
│   ├── api/
│   │   ├── quiz.py          # POST /quiz, GET /profile
│   │   ├── recommendations.py  # GET /recommendations/week
│   │   └── feedback.py      # POST /feedback
│   ├── services/
│   │   ├── podcast_index.py # Podcast Index API client + episode caching
│   │   ├── ollama.py        # Local LLM client
│   │   └── recommender.py   # Rule-based filter + LLM ranking
│   ├── db/
│   │   ├── database.py      # SQLite connection, session
│   │   └── models.py        # SQLAlchemy models
│   └── tests/
│       ├── test_quiz.py
│       ├── test_recommender.py
│       ├── test_podcast_index.py
│       └── test_feedback.py
└── frontend/
    ├── package.json
    └── src/
        ├── pages/
        │   ├── Quiz.jsx         # Multi-step onboarding quiz
        │   └── WeeklyView.jsx   # 7-day recommendation grid
        └── components/
            ├── EpisodeCard.jsx  # Artwork, title, reason, like/dislike
            ├── QuizStep.jsx     # Individual step wrapper
            └── FeedbackModal.jsx # Structured reasons + optional text
```

---

## Data Model (SQLite)

### `user_profile`
- `id`, `created_at`, `updated_at`
- `age_range` (optional), `location_region` (optional)
- `interest_categories` JSON: `[{category, intensity_1_to_5}]`
- `goals` JSON: `{primary, secondary[]}`
  - values: `learn / entertain / stay_informed / professional / relax`
- `preferred_formats` JSON array: `interview / narrative / solo / panel / news`
- `preferred_length_bucket`: `under_20 / 20_to_45 / over_45 / no_preference`
- `complexity_level`: `beginner / balanced / deep_dive`
- `trending_vs_timeless`: `trending / timeless / mixed`
- `mainstream_vs_niche`: `mainstream / niche / no_preference`
- `preferred_listen_schedule` JSON: `{monday: [morning, evening], tuesday: [...], ...}`

### `episodes`
- `id`, `podcast_index_id`, `podcast_id`, `fetched_at`
- `title`, `description`, `duration_sec`, `published_at`, `audio_url`, `artwork_url`
- `categories` JSON array
- `topic_tags` JSON array
- `content_format`: `interview / narrative / solo / panel / news`
- `complexity_level`: `beginner / balanced / advanced`
- `sentiment`: `uplifting / serious / neutral / funny`
- `host_name`, `guest_names` JSON array

### `recommendations`
- `id`, `week_of` (Monday date), `day_of_week`, `rank` (1–3)
- `episode_id` FK
- `score` float, `matched_criteria` JSON array
- `llm_reason` text, `llm_model_version`
- `was_listened` bool default false

### `feedback`
- `id`, `episode_id` FK, `created_at`
- `reaction`: `like / dislike / skip / neutral`
- `completion_pct` int (0–100), `did_finish` bool
- `listen_context`: `commute / workout / cooking / relaxing / other`
- Structured reasons (bool flags): `too_long`, `too_short`, `great_storytelling`,
  `poor_audio`, `fascinating_topic`, `too_basic`, `too_advanced`,
  `loved_guest`, `repetitive`, `great_production`
- `reason_text` text (optional free text)

---

## Quiz Flow (9 Steps)

| Step | Question | Input type |
|------|----------|-----------|
| 1 | Topic interests | Checkbox grid (~20 categories) + intensity slider per selection |
| 2 | Goals | Card select (primary + secondary) |
| 3 | Format preference | Card select (multi) |
| 4 | Episode length | Card select |
| 5 | Complexity | Card select |
| 6 | Trending vs. timeless | Card select |
| 7 | Mainstream vs. niche | Card select |
| 8 | Listening schedule | Weekly grid — toggle AM/PM/Evening per day |
| 9 | Demographics | Age range + location (skippable) |

---

## Recommendation Engine

**Step 1 — Fetch candidates** (`podcast_index.py`)
Query Podcast Index API using interest categories + format preferences. Cache results in `episodes` table to avoid redundant fetches.

**Step 2 — Rule-based filter** (`recommender.py`)
Filter candidates by: length bucket, complexity level, recency preference (trending vs. timeless), mainstream vs. niche popularity score.

**Step 3 — LLM ranking** (`ollama.py`)
Pass top N candidates + full user profile + recent feedback history to Ollama. Prompt asks LLM to rank and explain why each episode fits the user's goals and context. Returns top 3 per day distributed across listening schedule.

**Step 4 — Store + serve** (`recommendations.py`)
Persist ranked results to `recommendations` table. Frontend fetches via `GET /recommendations/week`.

---

## Feature Build Order (Phase-by-Phase with Tests)

| Phase | Feature | Definition of done |
|-------|---------|-------------------|
| 0 | **Project scaffold** | `uv init`, FastAPI serves `/health`, Vite app loads, Ollama install guide in README |
| 1 | **Quiz backend** | `POST /quiz` saves profile, `GET /profile` returns it; pytest passes |
| 2 | **Quiz frontend** | All 9 steps render, validate, submit to backend; manual test passes |
| 3 | **Podcast Index integration** | Search returns episodes, caching works; pytest with mocked API passes |
| 4 | **Rule-based recommender** | Given a profile, returns filtered ranked candidates; pytest passes |
| 5 | **Ollama integration** | LLM receives prompt + returns ranked list with reasons; pytest with mocked Ollama passes |
| 6 | **Weekly view UI** | 7-day grid renders with episode cards, artwork, and LLM reason text |
| 7 | **Feedback system** | Like/dislike + structured reasons saved; `POST /feedback` tested |
| 8 | **Feedback loop** | Profile weighted by feedback history; next week's recs differ; pytest passes |

---

## Verification (End-to-End)

1. `make install` — installs all deps via uv, pulls Ollama model
2. `make dev` — starts FastAPI on :8000 and Vite on :5173
3. Open browser → complete quiz → submit
4. `GET /recommendations/week` returns 21 episodes (3/day × 7 days) with reasons
5. Submit feedback for 3 episodes
6. Advance week → verify recommendations differ from week 1
7. `make test` — all pytest and Vitest suites pass
