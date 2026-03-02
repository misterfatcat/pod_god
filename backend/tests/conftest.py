import os

# Override DATABASE_URL before any backend module imports database.py.
# This ensures every test run uses a dedicated test database file,
# never the dev database (podcast_sort.db) that holds your real account.
os.environ["DATABASE_URL"] = "sqlite:///./podcast_sort_test.db"
