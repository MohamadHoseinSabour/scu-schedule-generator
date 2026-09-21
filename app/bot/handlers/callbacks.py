"""Callback query handlers for inline keyboard buttons."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.bot.messages.texts import REBUILD_MESSAGE

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "rebuild")
async def rebuild_callback(callback: CallbackQuery) -> None:
    """Handle the 'rebuild' button press."""
    await callback.answer()
    await callback.message.answer(REBUILD_MESSAGE)


@router.callback_query(F.data == "get_html")
async def get_html_callback(callback: CallbackQuery) -> None:
    """Handle the 'get HTML' button press."""
    await callback.answer()
    await callback.message.answer("📄 فایل Report رو دوباره ارسال کن تا HTML جدید بسازم.")


@router.callback_query(F.data == "share")
async def share_callback(callback: CallbackQuery) -> None:
    """Handle the 'share' button press (analytics tracking)."""
    await callback.answer()
    user_id = callback.from_user.id if callback.from_user else 0
    logger.info("Share button clicked by user %s", user_id)
    # TODO: Track share_button_click event in analytics DB
