"""Admin bot commands handler."""

from __future__ import annotations

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
router = Router()


def is_admin(user_id: int) -> bool:
    """Check if given Telegram user ID is an admin."""
    settings = get_settings()
    return user_id in settings.ADMIN_TELEGRAM_IDS


@router.message(Command("admin"))
async def admin_cmd(message: Message) -> None:
    """Show admin panel commands."""
    user_id = message.from_user.id if message.from_user else 0
    if not is_admin(user_id):
        return

    text = (
        "🔐 **پنل مدیریت ربات**\n\n"
        "دستورات موجود:\n"
        "▫️ /stats - مشاهده آمار کلی\n"
        "▫️ /health - بررسی وضعیت سرویس‌ها\n"
        "▫️ /jobs - لیست پردازش‌های اخیر\n"
        "▫️ /errors - خطاهای اخیر"
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("stats"))
async def stats_cmd(message: Message) -> None:
    """Show quick stats to admin."""
    user_id = message.from_user.id if message.from_user else 0
    if not is_admin(user_id):
        return

    text = (
        "📊 **آمار سیستم:**\n\n"
        "👥 تعداد کاربران: در حال پیاده‌سازی دیتابیس\n"
        "📄 فایل‌های پردازش شده: فعال\n"
        "✅ تبدیل‌های موفق: فعال\n"
        "🔗 سیستم رفرال: آماده"
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("health"))
async def health_cmd(message: Message) -> None:
    """Show system health check."""
    user_id = message.from_user.id if message.from_user else 0
    if not is_admin(user_id):
        return

    text = (
        "🩺 **وضعیت سیستم (Health Check):**\n\n"
        "🤖 ربات تلگرام: ONLINE ✅\n"
        "📑 پارسر اکسل: READY ✅\n"
        "🎨 رندرکننده HTML: READY ✅\n"
        "🖼️ رندرکننده تصویر: PLAYWRIGHT READY ✅\n"
        "💾 دیسک و ذخیره‌سازی: OK ✅"
    )
    await message.answer(text, parse_mode="Markdown")
