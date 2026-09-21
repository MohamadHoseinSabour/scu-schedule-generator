"""Application entry point for running the SCU Schedule Generator."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from app.config.settings import get_settings
from app.db.session import init_db

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("scu_schedule")


async def run_bot_only() -> None:
    """Run standalone Telegram bot polling worker."""
    settings = get_settings()

    if not settings.BOT_TOKEN:
        logger.error("BOT_TOKEN is not configured! Please set it in .env file or environment variables.")
        return

    for dir_name in ["storage/uploads", "storage/outputs", "storage/temp"]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)

    await init_db()

    from app.bot.bot import create_bot, create_dispatcher

    bot = create_bot(settings.BOT_TOKEN)
    dp = create_dispatcher()

    logger.info("SCU Schedule Generator Bot (standalone worker) starting in %s mode...", settings.APP_ENV)
    await dp.start_polling(bot)


def main() -> None:
    """Main launcher: starts standalone bot or integrated web+bot server."""
    settings = get_settings()
    mode = os.getenv("MODE", "all").lower()

    if "--bot-only" in sys.argv or mode == "bot":
        asyncio.run(run_bot_only())
        return

    # In Railway / production / integrated mode:
    # Run Uvicorn ASGI server which binds to $PORT and runs both API and Bot (via lifespan)
    import uvicorn

    port = int(os.getenv("PORT", settings.PORT))
    logger.info(
        "Starting SCU Schedule Generator integrated server on 0.0.0.0:%d (%s mode)...",
        port,
        settings.APP_ENV,
    )
    uvicorn.run(
        "app.admin.routes:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
