"""Tests for database models and session initialization."""

import pytest
from sqlalchemy import select
from app.db.models import User, Job
from app.db.session import init_db, get_session_factory


@pytest.mark.asyncio
async def test_database_initialization_and_user_crud():
    await init_db()
    session_factory = get_session_factory()

    async with session_factory() as session:
        import random
        test_id = random.randint(1000000, 999999999)
        # Create a user
        user = User(
            telegram_id=test_id,
            username="test_student",
            first_name="Ali",
            referral_code=f"ref_{test_id}",
        )
        session.add(user)
        await session.commit()

        # Query the user
        stmt = select(User).where(User.telegram_id == test_id)
        saved_user = (await session.execute(stmt)).scalar_one()

        assert saved_user.id is not None
        assert saved_user.username == "test_student"
        assert saved_user.referral_code == f"ref_{test_id}"
