from backend.db.database import engine, Base
from backend.db import models  # noqa: F401 - registers models


def test_db_creates_tables():
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "user_profile" in tables
    assert "episodes" in tables
    assert "recommendations" in tables
    assert "feedback" in tables
