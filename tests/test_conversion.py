"""Tests for ConversionService (Phase 4)."""

from pathlib import Path
import pytest
from app.render.html_renderer import HTMLRenderer
from app.services.conversion_service import ConversionService


@pytest.mark.asyncio
async def test_conversion_service_with_golden_file(tmp_path):
    renderer = HTMLRenderer()
    service = ConversionService(
        html_renderer=renderer,
        image_renderer=None,  # image rendering can be mocked or tested separately
        output_dir=tmp_path,
        bot_username="TestBot",
    )

    report_file = Path("ReferenceS/Report.xls")
    result = await service.convert(report_file)

    assert result.error is None
    assert result.job_id.startswith("JOB-")
    assert result.report is not None
    assert result.report.total_courses == 9
    assert result.report.total_units == 20.0
    assert result.html_path is not None
    assert result.html_path.exists()
    assert result.html_path.stat().st_size > 0

    # Validate output HTML content
    html_content = result.html_path.read_text(encoding="utf-8")
    assert "الکترونیک 2" in html_content
    assert "مدارهای منطقی" in html_content
    assert result.has_conflicts is False
