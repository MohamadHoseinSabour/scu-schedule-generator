"""Handler for /start command with deep link referral support."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.main import main_keyboard
from app.bot.messages.texts import WELCOME_MESSAGE

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start with optional deep link referral code.

    Example: ``/start ref_A83KD``
    """
    user = message.from_user
    logger.info(
        "User %s (%s) started the bot",
        user.id if user else "unknown",
        user.username if user else "unknown",
    )

    # Extract referral code if present
    args = message.text.split(maxsplit=1) if message.text else []
    if len(args) > 1 and args[1].startswith("ref_"):
        ref_code = args[1]
        logger.info("Referral code received: %s from user %s", ref_code, user.id if user else "?")
        # TODO: Process referral when DB is ready

    await message.answer(WELCOME_MESSAGE, reply_markup=main_keyboard())
