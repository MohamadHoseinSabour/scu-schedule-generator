"""File Service – upload validation, temp storage, hashing and cleanup."""

from __future__ import annotations

import hashlib
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import aiofiles

logger = logging.getLogger(__name__)

# Allowed upload formats
ALLOWED_EXTENSIONS: set[str] = {".xls", ".xlsx"}


class FileService:
    """Handles file validation, temporary storage, and lifecycle management."""

    async def validate_upload(
        self,
        file_name: str | None,
        file_size: int,
        max_size_mb: int = 10,
    ) -> tuple[bool, str]:
        """Validate an uploaded file's name and size.

        Returns
        -------
        tuple[bool, str]
            ``(True, "")`` on success, ``(False, error_message)`` on failure.
        """
        if not file_name:
            return False, "❌ نام فایل مشخص نیست."

        ext = Path(file_name).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return (
                False,
                "❌ این فایل قابل پردازش نیست.\n\n"
                "لطفاً فایل Report اصلی دانشگاه رو با فرمت Excel ارسال کن.",
            )

        max_bytes = max_size_mb * 1024 * 1024
        if file_size > max_bytes:
            return (
                False,
                f"❌ حجم فایل بیش از حد مجاز ({max_size_mb}MB) است.",
            )

        if file_size == 0:
            return False, "❌ فایل خالی است."

        return True, ""

    async def save_temp(
        self,
        file_data: bytes,
        original_name: str,
        temp_dir: Path,
    ) -> Path:
        """Save uploaded bytes to a temp directory with a UUID filename.

        Preserves the original extension.
        """
        temp_dir.mkdir(parents=True, exist_ok=True)
        ext = Path(original_name).suffix.lower()
        filename = f"{uuid.uuid4().hex}{ext}"
        dest = temp_dir / filename

        async with aiofiles.open(dest, "wb") as f:
            await f.write(file_data)

        logger.info("Saved temp file: %s (%d bytes)", dest, len(file_data))
        return dest

    async def compute_hash(self, file_path: Path) -> str:
        """Compute the SHA-256 hex digest of *file_path*."""
        sha = hashlib.sha256()
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                sha.update(chunk)
        return sha.hexdigest()

    async def cleanup_old_files(
        self,
        directory: Path,
        ttl_hours: int = 24,
    ) -> int:
        """Delete files in *directory* older than *ttl_hours*.

        Returns the number of files deleted.
        """
        if not directory.exists():
            return 0

        cutoff = datetime.now() - timedelta(hours=ttl_hours)
        deleted = 0

        for fpath in directory.iterdir():
            if fpath.is_file():
                mtime = datetime.fromtimestamp(fpath.stat().st_mtime)
                if mtime < cutoff:
                    fpath.unlink()
                    deleted += 1
                    logger.debug("Deleted expired file: %s", fpath)

        if deleted:
            logger.info("Cleaned up %d expired files from %s", deleted, directory)
        return deleted
