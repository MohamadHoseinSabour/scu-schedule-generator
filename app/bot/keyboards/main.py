"""Telegram keyboard definitions."""

from __future__ import annotations

from urllib.parse import quote

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.bot.messages.texts import SHARE_TEXT


def main_keyboard() -> ReplyKeyboardMarkup:
    """Main reply keyboard shown after /start."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 ارسال تاییدیه انتخاب واحد")],
            [KeyboardButton(text="🌐 ورود به سامانه دانشگاه (به‌زودی)")],
            [
                KeyboardButton(text="📖 راهنمای دریافت فایل"),
                KeyboardButton(text="🎁 معرفی به دوستان"),
            ],
        ],
        resize_keyboard=True,
    )


def result_inline_keyboard(
    bot_username: str,
    referral_code: str = "",
) -> InlineKeyboardMarkup:
    """Inline keyboard shown under the result photo."""
    ref_param = f"?start=ref_{referral_code}" if referral_code else ""
    bot_link = f"https://t.me/{bot_username}{ref_param}"
    share_url = (
        f"https://t.me/share/url"
        f"?url={quote(bot_link)}"
        f"&text={quote(SHARE_TEXT)}"
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📤 ارسال به دوستان", url=share_url),
                InlineKeyboardButton(text="🔄 ساخت مجدد", callback_data="rebuild"),
            ]
        ]
    )
