"""Referral and Share system service."""

from __future__ import annotations

import secrets
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Referral, ShareEvent, User


class ShareService:
    """Manages referral code generation, deep-link attribution, and share telemetry."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def generate_referral_code() -> str:
        """Generate a random unique referral code like ref_A83KD."""
        random_suffix = secrets.token_hex(3).upper()[:5]
        return f"ref_{random_suffix}"

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        referred_by_code: Optional[str] = None,
    ) -> User:
        """Find an existing user by telegram_id or register a new user with referral tracking."""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is not None:
            if username and user.username != username:
                user.username = username
            if first_name and user.first_name != first_name:
                user.first_name = first_name
            await self.session.commit()
            return user

        # Register new user
        new_code = self.generate_referral_code()
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            referral_code=new_code,
            referred_by=referred_by_code,
        )
        self.session.add(user)
        await self.session.flush()

        # If user joined via someone's referral code, link them
        if referred_by_code:
            ref_stmt = select(User).where(User.referral_code == referred_by_code)
            referrer = (await self.session.execute(ref_stmt)).scalar_one_or_none()
            if referrer and referrer.id != user.id:
                referral_entry = Referral(
                    referrer_user_id=referrer.id,
                    referred_user_id=user.id,
                )
                self.session.add(referral_entry)

        await self.session.commit()
        return user

    async def track_share_click(self, user_id: int) -> None:
        """Log a share button click event."""
        event = ShareEvent(user_id=user_id, type="share_click")
        self.session.add(event)
        await self.session.commit()
