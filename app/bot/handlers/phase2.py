"""Phase 2 handler – portal login (currently disabled via feature flag) and menu buttons."""

from __future__ import annotations

import os
from aiogram import F, Router
from aiogram.types import Message

from app.bot.messages.texts import (
    EXCEL_GUIDE_MESSAGE,
    HELP_MESSAGE,
    PORTAL_DISABLED_MESSAGE,
)

router = Router()


@router.message(F.text.in_({"🌐 ورود به سامانه دانشگاه (به‌زودی)", "🌐 ورود به سامانه دانشگاه"}))
async def portal_handler(message: Message) -> None:
    """Respond when user taps the portal login button."""
    await message.answer(PORTAL_DISABLED_MESSAGE)


@router.message(F.text.in_({"📄 ارسال تاییدیه انتخاب واحد", "📄 ساخت برنامه از Excel"}))
async def excel_guide(message: Message) -> None:
    """Prompt user to upload their confirmation file."""
    await message.answer(EXCEL_GUIDE_MESSAGE)


@router.message(F.text.in_({"📖 راهنمای دریافت فایل", "ℹ️ راهنما"}))
async def help_handler(message: Message) -> None:
    """Show detailed help message."""
    await message.answer(HELP_MESSAGE)


@router.message(F.text.in_({"🎁 معرفی به دوستان", "📤 معرفی ربات"}))
async def share_handler(message: Message) -> None:
    """Show share and referral invite message."""
    bot_username = os.getenv("BOT_USERNAME", "")
    bot_link = f"https://t.me/{bot_username}" if bot_username else "این ربات"
    text = (
        "🎁 <b>معرفی به هم‌دانشگاهی‌ها</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "با معرفی این ربات به دوستانت، اون‌ها هم می‌تونن برنامه‌شون رو تمیز و زیبا مرتب کنن! 🤩\n\n"
        f"🔗 <b>لینک ورود به ربات:</b>\n"
        f"{bot_link}\n\n"
        "<i>کافیه لینک بالا یا خروجی برنامه‌ت رو برای دوستات فوروارد کنی! ✨</i>"
    )
    await message.answer(text)
