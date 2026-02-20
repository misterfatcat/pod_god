import pytest
from fastapi.testclient import TestClient
from backend.services.auth import hash_password, verify_password, create_access_token, decode_access_token
from backend.main import app
from backend.db.database import engine, Base
from backend.db import models  # noqa


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_password_round_trip():
    hashed = hash_password("mysecret")
    assert verify_password("mysecret", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_round_trip():
    token = create_access_token({"sub": "42"})
    payload = decode_access_token(token)
    assert payload["sub"] == "42"


def test_expired_token_returns_none():
    from datetime import timedelta
    token = create_access_token({"sub": "42"}, expires_delta=timedelta(seconds=-1))
    assert decode_access_token(token) is None


def test_register_returns_token():
    resp = client.post("/auth/register", json={"email": "test@example.com", "password": "secret123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email_returns_400():
    client.post("/auth/register", json={"email": "test@example.com", "password": "secret123"})
    resp = client.post("/auth/register", json={"email": "test@example.com", "password": "other"})
    assert resp.status_code == 400


def test_login_returns_token():
    client.post("/auth/register", json={"email": "test@example.com", "password": "secret123"})
    resp = client.post("/auth/login", json={"email": "test@example.com", "password": "secret123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password_returns_401():
    client.post("/auth/register", json={"email": "test@example.com", "password": "secret123"})
    resp = client.post("/auth/login", json={"email": "test@example.com", "password": "wrong"})
    assert resp.status_code == 401
