"""Asynchronous Celery tasks for heavy conversions and storage maintenance."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from celery import Celery

from app.config.settings import get_settings
from app.services.conversion_service import ConversionService
from app.services.file_service import FileService
from app.render.html_renderer import HTMLRenderer

logger = logging.getLogger(__name__)

settings = get_settings()
celery_app = Celery("scu_schedule_tasks", broker=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="tasks.process_schedule_task", bind=True, max_retries=2)
def process_schedule_task(self, file_path_str: str, bot_username: str = "") -> dict:
    """Asynchronously process an Excel schedule report."""
    file_path = Path(file_path_str)
    renderer = HTMLRenderer()

    # In production worker, Playwright can be initialized
    service = ConversionService(
        html_renderer=renderer,
        image_renderer=None,
        output_dir=Path("storage/outputs"),
        bot_username=bot_username,
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(service.convert(file_path))
        return {
            "job_id": result.job_id,
            "success": result.error is None,
            "html_path": str(result.html_path) if result.html_path else None,
            "image_path": str(result.image_path) if result.image_path else None,
            "error": result.error,
        }
    finally:
        loop.close()


@celery_app.task(name="tasks.cleanup_expired_files_task")
def cleanup_expired_files_task() -> int:
    """Purge temporary uploads and generated files exceeding TTL."""
    file_service = FileService()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        deleted_temp = loop.run_until_complete(
            file_service.cleanup_old_files(Path("storage/temp"), ttl_hours=settings.OUTPUT_TTL_HOURS)
        )
        deleted_out = loop.run_until_complete(
            file_service.cleanup_old_files(Path("storage/outputs"), ttl_hours=settings.OUTPUT_TTL_HOURS)
        )
        return deleted_temp + deleted_out
    finally:
        loop.close()
