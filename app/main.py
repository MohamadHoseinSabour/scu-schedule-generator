"""Application entry point for running the SCU Schedule Generator Bot."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from app.bot.bot import create_bot, create_dispatcher
from app.config.settings import get_settings

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("scu_schedule")


async def main() -> None:
    """Initialize directories and start Telegram bot polling."""
    settings = get_settings()

    if not settings.BOT_TOKEN:
        logger.error("BOT_TOKEN is not configured! Please set it in .env file.")
        return

    # Ensure storage directories exist
    for dir_name in ["storage/uploads", "storage/outputs", "storage/temp"]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)

    bot = create_bot(settings.BOT_TOKEN)
    dp = create_dispatcher()

    logger.info("SCU Schedule Generator Bot starting in %s mode...", settings.APP_ENV)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
