"""Tests for ShareService and Referral tracking."""

import pytest
from app.db.session import init_db, get_session_factory
from app.services.share_service import ShareService


@pytest.mark.asyncio
async def test_referral_flow():
    await init_db()
    session_factory = get_session_factory()

    import random
    id1 = random.randint(10000000, 49999999)
    id2 = random.randint(50000000, 99999999)

    async with session_factory() as session:
        share_service = ShareService(session)

        # 1. Register referrer
        user1 = await share_service.get_or_create_user(
            telegram_id=id1,
            username="referrer_user",
            first_name="User1",
        )
        assert user1.referral_code.startswith("ref_")

        # 2. Register referee using user1's code
        user2 = await share_service.get_or_create_user(
            telegram_id=id2,
            username="referee_user",
            first_name="User2",
            referred_by_code=user1.referral_code,
        )
        assert user2.referred_by == user1.referral_code

        # 3. Track share click
        await share_service.track_share_click(user1.id)
