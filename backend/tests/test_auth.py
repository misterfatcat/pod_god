from backend.services.auth import hash_password, verify_password, create_access_token, decode_access_token


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
