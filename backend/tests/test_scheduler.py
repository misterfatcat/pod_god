from unittest.mock import AsyncMock, MagicMock, patch
import pytest


@pytest.fixture
def mock_users():
    user1 = MagicMock()
    user1.id = 1
    user2 = MagicMock()
    user2.id = 2
    return [user1, user2]


@pytest.mark.asyncio
async def test_scheduler_calls_generate_for_each_user(mock_users):
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = mock_users

    mock_generate = AsyncMock(return_value={"week_of": "2025-02-17", "recommendations": {}})

    with patch("backend.services.scheduler.SessionLocal", return_value=mock_db), \
         patch("backend.api.recommendations._generate_for_user", mock_generate):
        from backend.services.scheduler import _generate_all_users
        await _generate_all_users()

    assert mock_generate.call_count == 2
    called_user_ids = [call.args[0] for call in mock_generate.call_args_list]
    assert 1 in called_user_ids
    assert 2 in called_user_ids


@pytest.mark.asyncio
async def test_scheduler_continues_if_one_user_fails(mock_users):
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = mock_users

    call_count = 0

    async def side_effect(user_id, db):
        nonlocal call_count
        call_count += 1
        if user_id == 1:
            raise RuntimeError("Simulated failure for user 1")
        return {"week_of": "2025-02-17", "recommendations": {}}

    with patch("backend.services.scheduler.SessionLocal", return_value=mock_db), \
         patch("backend.api.recommendations._generate_for_user", side_effect=side_effect):
        from backend.services.scheduler import _generate_all_users
        await _generate_all_users()

    # Both users were attempted, even though user 1 failed
    assert call_count == 2
