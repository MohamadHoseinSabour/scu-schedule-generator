"""Phase 2 handler – portal login (currently disabled via feature flag)."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

from app.bot.messages.texts import PORTAL_DISABLED_MESSAGE, HELP_MESSAGE

router = Router()


@router.message(F.text == "🌐 ورود به سامانه دانشگاه")
async def portal_handler(message: Message) -> None:
    """Respond when user taps the portal login button.

    Currently disabled – ``PORTAL_ENABLED=false``.
    No actual login is performed.
    """
    # TODO: Check FeatureFlags.PORTAL_ENABLED and branch accordingly
    await message.answer(PORTAL_DISABLED_MESSAGE)


@router.message(F.text == "📄 ساخت برنامه از Excel")
async def excel_guide(message: Message) -> None:
    """Prompt user to upload their Excel report."""
    await message.answer("📄 فایل Report دانشگاهت رو همینجا ارسال کن.")


@router.message(F.text == "ℹ️ راهنما")
async def help_handler(message: Message) -> None:
    """Show help message."""
    await message.answer(HELP_MESSAGE)


@router.message(F.text == "📤 معرفی ربات")
async def share_handler(message: Message) -> None:
    """Show share info."""
    import os
    bot_username = os.getenv("BOT_USERNAME", "")
    await message.answer(
        f"📤 این ربات رو به دوستات معرفی کن:\n\n"
        f"https://t.me/{bot_username}"
    )
