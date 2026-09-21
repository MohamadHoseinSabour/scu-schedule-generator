"""Callback query handlers for inline keyboard buttons."""

from __future__ import annotations

import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery

from app.bot.messages.texts import REBUILD_MESSAGE

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "rebuild")
async def rebuild_callback(callback: CallbackQuery) -> None:
    """Handle the 'rebuild' button press."""
    await callback.answer()
    if callback.message:
        await callback.message.answer(REBUILD_MESSAGE)


@router.callback_query(F.data.startswith("get_html:"))
async def get_html_on_demand_callback(callback: CallbackQuery) -> None:
    """Send the HTML file when the user taps the on-demand download button."""
    if not callback.data:
        return

    file_stem = callback.data.split(":", 1)[1].strip()

    # Security check: only alphanumeric stem to avoid path traversal
    if not file_stem.isalnum():
        await callback.answer("❌ شناسه فایل نامعتبر است.", show_alert=True)
        return

    html_path = Path("storage/outputs") / f"{file_stem}.html"
    if not html_path.exists():
        await callback.answer(
            "⚠️ این فایل منقضی شده است. لطفاً فایل اکسل تاییدیه را دوباره بفرستید.",
            show_alert=True,
        )
        return

    await callback.answer("📥 در حال ارسال فایل HTML...")

    if callback.message:
        html_bytes = html_path.read_bytes()
        await callback.message.answer_document(
            BufferedInputFile(html_bytes, filename="barname_haftegi.html"),
            caption=(
                "🌐 <b>نسخه کامل و تعاملی برنامه هفتگی (HTML)</b>\n"
                "<i>این فایل رو می‌تونی با هر مرورگری توی گوشی یا کامپیوتر باز کنی و حتی آدرس کلاس‌ها یا یادداشت‌هات رو داخلش ویرایش کنی. ✨</i>"
            ),
        )


@router.callback_query(F.data == "get_html")
async def get_html_legacy_callback(callback: CallbackQuery) -> None:
    """Handle generic get_html callback."""
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "📄 برای دریافت نسخه جدید HTML، فایل اکسل تاییدیه انتخاب واحد را ارسال کنید."
        )


@router.callback_query(F.data == "share")
async def share_callback(callback: CallbackQuery) -> None:
    """Handle the 'share' button press (analytics tracking)."""
    await callback.answer()
    user = callback.from_user
    if not user:
        return

    logger.info("Share button clicked by user %s", user.id)
    try:
        from app.db.session import get_session_factory
        from app.services.share_service import ShareService

        session_factory = get_session_factory()
        async with session_factory() as session:
            share_service = ShareService(session)
            db_user = await share_service.get_or_create_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
            )
            await share_service.track_share_click(db_user.id)
    except Exception:
        logger.exception("Failed to record share event for user %s", user.id)
