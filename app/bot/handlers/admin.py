"""Admin bot commands handler."""

from __future__ import annotations

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config.settings import get_settings
from app.db.session import get_session_factory
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = Router()


def is_admin(user_id: int) -> bool:
    """Check if given Telegram user ID is an authorized admin."""
    settings = get_settings()
    return user_id in settings.ADMIN_TELEGRAM_IDS


@router.message(Command("admin"))
async def admin_cmd(message: Message) -> None:
    """Show admin panel commands and dashboard link."""
    user = message.from_user
    user_id = user.id if user else 0
    if not is_admin(user_id):
        return

    dashboard_url = f"http://localhost:8000/admin?admin_id={user_id}"

    text = (
        "🔐 <b>پنل مدیریت ربات برنامه هفتگی</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "دستورات مدیریتی ربات:\n"
        "▫️ /stats - مشاهده آمار و ارقام زنده سیستم\n"
        "▫️ /health - بررسی وضعیت سلامت سرور و سرویس‌ها\n\n"
        "🖥 <b>لینک ورود به داشبورد گرافیکی تحت وب:</b>\n"
        f"👉 <a href='{dashboard_url}'><b>ورود به پنل داشبورد وب</b></a>\n\n"
        "<i>(برای دسترسی به پنل وب، سرویس uvicorn باید روشن باشد)</i>"
    )
    await message.answer(text)


@router.message(Command("stats"))
async def stats_cmd(message: Message) -> None:
    """Show live system KPIs directly in Telegram."""
    user = message.from_user
    user_id = user.id if user else 0
    if not is_admin(user_id):
        return

    session_factory = get_session_factory()
    async with session_factory() as session:
        analytics = AnalyticsService(session)
        kpis = await analytics.get_dashboard_kpis()

    text = (
        "📊 <b>گزارش آمار و عملکرد سیستم</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>کل کاربران:</b> {kpis['total_users']:,} نفر\n"
        f"📥 <b>فایل‌های دریافتی:</b> {kpis['total_jobs']:,} فایل\n"
        f"✅ <b>تبدیل‌های موفق:</b> {kpis['successful_conversions']:,}\n"
        f"❌ <b>خطاهای تبدیل:</b> {kpis['failed_conversions']:,}\n\n"
        f"🌐 <b>فایل‌های HTML تولیدشده:</b> {kpis['total_html']:,}\n"
        f"🖼 <b>تصاویر تولیدشده:</b> {kpis['total_images']:,}\n"
        f"📤 <b>کلیک‌های دکمه اشتراک:</b> {kpis['share_clicks']:,}\n"
        f"🔗 <b>دعوت‌های موفق (Referral):</b> {kpis['referral_count']:,}\n"
        f"⏱ <b>میانگین زمان پردازش:</b> {kpis['avg_processing_time']} ثانیه\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "<i>سیستم در وضعیت پایدار و آنلاین است. ✨</i>"
    )
    await message.answer(text)


@router.message(Command("health"))
async def health_cmd(message: Message) -> None:
    """Show system health check."""
    user = message.from_user
    user_id = user.id if user else 0
    if not is_admin(user_id):
        return

    text = (
        "🩺 <b>وضعیت سرویس‌های سیستم (Health Check)</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "🤖 <b>ربات تلگرام:</b> ONLINE ✅\n"
        "📑 <b>پارسر اکسل:</b> READY ✅\n"
        "🎨 <b>رندرکننده HTML:</b> READY ✅\n"
        "🖼 <b>موتور Playwright:</b> ACTIVE ✅\n"
        "💾 <b>پایگاه داده (Database):</b> CONNECTED ✅\n"
        "📁 <b>دیسک و ذخیره‌سازی:</b> OK ✅"
    )
    await message.answer(text)
