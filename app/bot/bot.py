"""Bot instance initialization and dispatcher configuration."""

from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


def create_bot(token: str) -> Bot:
    """Create and configure an aiogram Bot instance."""
    return Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """Create and configure the aiogram Dispatcher with registered routers."""
    dp = Dispatcher()

    from app.bot.handlers import admin, callbacks, phase2, start, upload

    dp.include_router(start.router)
    dp.include_router(upload.router)
    dp.include_router(callbacks.router)
    dp.include_router(phase2.router)
    dp.include_router(admin.router)

    return dp
