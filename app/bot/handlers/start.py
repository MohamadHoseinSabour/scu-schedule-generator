"""Handler for /start command with deep link referral support."""

from __future__ import annotations

import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.main import main_keyboard
from app.bot.messages.texts import WELCOME_MESSAGE
from app.db.session import get_session_factory
from app.services.share_service import ShareService

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start with optional deep link referral code.

    Example: ``/start ref_A83KD``
    """
    user = message.from_user
    if not user:
        return

    logger.info("User %s (@%s) started the bot", user.id, user.username or "no_username")

    # Extract referral code if present
    args = message.text.split(maxsplit=1) if message.text else []
    ref_code: str | None = None
    if len(args) > 1 and args[1].startswith("ref_"):
        ref_code = args[1].strip()
        logger.info("Referral code %s received from user %s", ref_code, user.id)

    # Persist user and referral in database
    try:
        session_factory = get_session_factory()
        async with session_factory() as session:
            share_service = ShareService(session)
            await share_service.get_or_create_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                referred_by_code=ref_code,
            )
    except Exception:
        logger.exception("Error registering user %s in database during /start", user.id)

    await message.answer(WELCOME_MESSAGE, reply_markup=main_keyboard())
