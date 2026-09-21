"""Handler for Excel file uploads – the main bot feature."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from aiogram import F, Router
from aiogram.types import BufferedInputFile, Message

from app.bot.keyboards.main import result_inline_keyboard
from app.bot.messages.texts import (
    CONFLICT_WARNING,
    ERROR_MESSAGE,
    FUN_COMPLETION,
    PROCESSING_BUILDING,
    PROCESSING_CHECKING,
    PROCESSING_DONE,
    PROCESSING_IMAGE,
    PROCESSING_RECEIVED,
    SUCCESS_TEMPLATE,
)
from app.render.html_renderer import HTMLRenderer
from app.services.conversion_service import ConversionService
from app.services.file_service import FileService

logger = logging.getLogger(__name__)
router = Router()

_file_service = FileService()


@router.message(F.document)
async def handle_document(message: Message) -> None:
    """Process an uploaded confirmation Excel file."""
    doc = message.document
    if doc is None:
        return

    user = message.from_user
    user_id = user.id if user else 0
    logger.info("User %s uploaded file: %s (%d bytes)", user_id, doc.file_name, doc.file_size or 0)

    # 1. Validate file
    is_valid, error_msg = await _file_service.validate_upload(
        doc.file_name, doc.file_size or 0
    )
    if not is_valid:
        await message.answer(error_msg)
        return

    # 2. Send first progress message
    progress_msg = await message.answer(PROCESSING_RECEIVED)

    temp_path: Path | None = None
    try:
        # 3. Download file from Telegram
        bot = message.bot
        file_obj = await bot.get_file(doc.file_id)
        file_data = await bot.download_file(file_obj.file_path)

        # 4. Save to temp
        temp_dir = Path("storage/temp")
        temp_path = await _file_service.save_temp(
            file_data.read(), doc.file_name or "weekly_schedule.xls", temp_dir
        )

        # 5. Update progress
        await progress_msg.edit_text(PROCESSING_CHECKING)

        # 6. Run conversion pipeline
        html_renderer = HTMLRenderer()
        image_renderer = None
        try:
            from app.render.image_renderer import ImageRenderer
            image_renderer = ImageRenderer()
        except ImportError:
            logger.warning("Playwright not available, skipping server image generation")

        bot_username = os.getenv("BOT_USERNAME", "")

        conversion_service = ConversionService(
            html_renderer=html_renderer,
            image_renderer=image_renderer,
            output_dir=Path("storage/outputs"),
            bot_username=bot_username,
        )

        await progress_msg.edit_text(PROCESSING_BUILDING)
        result = await conversion_service.convert(temp_path)

        if result.error or not result.report:
            logger.error("Conversion error for user %s: %s", user_id, result.error)
            await progress_msg.edit_text(ERROR_MESSAGE)
            return

        # 7. Build summary text
        report = result.report
        summary = SUCCESS_TEMPLATE.format(
            total_courses=report.total_courses,
            total_units=int(report.total_units),
        )
        if result.has_conflicts:
            summary += "\n\n" + CONFLICT_WARNING

        # 8. Send outputs
        await progress_msg.edit_text(PROCESSING_DONE)

        html_stem = result.html_path.stem if result.html_path and result.html_path.exists() else ""

        # Send Image photo (or summary text fallback)
        if result.image_path and result.image_path.exists():
            img_bytes = result.image_path.read_bytes()
            await message.answer_photo(
                BufferedInputFile(img_bytes, filename="barname_haftegi.png"),
                caption=summary,
                reply_markup=result_inline_keyboard(bot_username, html_stem=html_stem),
            )
        else:
            await message.answer(
                summary,
                reply_markup=result_inline_keyboard(bot_username, html_stem=html_stem),
            )

        # 9. Send fun completion note
        await message.answer(FUN_COMPLETION)

        logger.info(
            "Job %s completed for user %s in %.2fs",
            result.job_id, user_id, result.processing_time,
        )

    except Exception:
        logger.exception("Unhandled error processing file for user %s", user_id)
        try:
            await progress_msg.edit_text(ERROR_MESSAGE)
        except Exception:
            pass
    finally:
        # 10. Cleanup temporary file
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)
