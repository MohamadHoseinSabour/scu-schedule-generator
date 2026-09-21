"""Conversion Service – central orchestrator for the schedule pipeline.

Coordinates parsing, validation, HTML generation, and image rendering.
"""

from __future__ import annotations

import logging
import secrets
import time as _time
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.models import ScheduleReport, ValidationResult
from app.domain.validation import validate_schedule
from app.parsers.base import ReportParser
from app.parsers.report_v1 import ReportV1Parser
from app.render.html_renderer import HTMLRenderer

logger = logging.getLogger(__name__)


class ConversionResult(BaseModel):
    """Result of a full conversion pipeline run."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    html_path: Optional[Path] = None
    image_path: Optional[Path] = None
    report: Optional[ScheduleReport] = None
    validation: Optional[ValidationResult] = None
    job_id: str = ""
    processing_time: float = 0.0
    has_conflicts: bool = False
    error: Optional[str] = None


class ConversionService:
    """Orchestrates the full Excel → Model → HTML/PNG pipeline."""

    def __init__(
        self,
        html_renderer: HTMLRenderer,
        image_renderer: object | None = None,
        output_dir: Path = Path("storage/outputs"),
        bot_username: str = "",
    ) -> None:
        self.html_renderer = html_renderer
        self.image_renderer = image_renderer
        self.output_dir = output_dir
        self.bot_username = bot_username
        self._parsers: list[ReportParser] = [ReportV1Parser()]

    async def convert(self, file_path: Path) -> ConversionResult:
        """Run the full conversion pipeline.

        Parameters
        ----------
        file_path:
            Path to the uploaded Excel file (.xls or .xlsx).

        Returns
        -------
        ConversionResult
            Contains paths to generated files, the parsed report, and metadata.
        """
        job_id = self._generate_job_id()
        start = _time.monotonic()
        logger.info("Job %s: starting conversion for %s", job_id, file_path.name)

        try:
            # 1. Detect format & open workbook
            workbook = self._open_workbook(file_path)

            # 2. Select parser
            parser = self._select_parser(workbook)
            if parser is None:
                return ConversionResult(
                    job_id=job_id,
                    processing_time=_time.monotonic() - start,
                    error="فرمت این فایل Excel پشتیبانی نمی‌شود.",
                )

            # 3. Parse
            report = parser.parse(workbook)
            logger.info(
                "Job %s: parsed %d courses, %.0f units",
                job_id,
                report.total_courses,
                report.total_units,
            )

            # 4. Validate
            validation = validate_schedule(report)
            has_conflicts = len(validation.conflicts) > 0

            # 5. Generate HTML
            self.output_dir.mkdir(parents=True, exist_ok=True)
            file_stem = secrets.token_hex(8)

            html_content = self.html_renderer.render_full(report)
            html_path = self.output_dir / f"{file_stem}.html"
            html_path.write_text(html_content, encoding="utf-8")
            logger.info("Job %s: HTML written to %s", job_id, html_path)

            # 6. Generate PNG (if image renderer available)
            image_path: Path | None = None
            if self.image_renderer is not None:
                try:
                    image_html = self.html_renderer.render_image(
                        report, bot_username=self.bot_username
                    )
                    image_path = self.output_dir / f"{file_stem}.png"
                    await self.image_renderer.render_to_file(image_html, image_path)
                    logger.info("Job %s: PNG written to %s", job_id, image_path)
                except Exception:
                    logger.exception("Job %s: image rendering failed", job_id)
                    image_path = None

            elapsed = _time.monotonic() - start
            logger.info("Job %s: completed in %.2fs", job_id, elapsed)

            return ConversionResult(
                html_path=html_path,
                image_path=image_path,
                report=report,
                validation=validation,
                job_id=job_id,
                processing_time=elapsed,
                has_conflicts=has_conflicts,
            )

        except Exception as exc:
            elapsed = _time.monotonic() - start
            logger.exception("Job %s: conversion failed", job_id)
            return ConversionResult(
                job_id=job_id,
                processing_time=elapsed,
                error=str(exc),
            )

    # -- helpers ------------------------------------------------------------

    def _open_workbook(self, file_path: Path) -> object:
        """Open an Excel workbook using the appropriate library."""
        ext = file_path.suffix.lower()
        if ext == ".xls":
            from app.parsers.xls_parser import read_xls

            return read_xls(file_path)
        elif ext == ".xlsx":
            from app.parsers.xlsx_parser import read_xlsx

            return read_xlsx(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    def _select_parser(self, workbook: object) -> ReportParser | None:
        """Find the first parser that can handle *workbook*."""
        for parser in self._parsers:
            if parser.can_parse(workbook):
                return parser
        return None

    @staticmethod
    def _generate_job_id() -> str:
        """Generate a unique job ID like ``JOB-20260921-A83K2``."""
        date_str = datetime.now().strftime("%Y%m%d")
        suffix = secrets.token_hex(3).upper()[:5]
        return f"JOB-{date_str}-{suffix}"
