"""Tests for HTMLRenderer (Phase 2)."""

from pathlib import Path
import pytest
from app.parsers.xls_parser import read_xls
from app.parsers.report_v1 import ReportV1Parser
from app.render.html_renderer import HTMLRenderer


@pytest.fixture
def golden_report():
    sample_path = Path("ReferenceS/Report.xls")
    wb = read_xls(sample_path)
    parser = ReportV1Parser()
    return parser.parse(wb)


def test_html_full_render(golden_report):
    renderer = HTMLRenderer()
    html_out = renderer.render_full(golden_report)

    assert "<html" in html_out
    assert 'dir="rtl"' in html_out
    assert "برنامه هفتگی من" in html_out
    assert "الکترونیک 2" in html_out
    assert "مدارهای منطقی" in html_out
    assert "ماشین های الکتریکی 2" in html_out
    assert "شنبه" in html_out
    assert "چهارشنبه" in html_out
    assert "تعطیل رسمی" in html_out  # Full version has Thursday/Friday as holiday
    assert "html2canvas" in html_out


def test_html_image_render_no_thursday_no_friday(golden_report):
    renderer = HTMLRenderer()
    img_html = renderer.render_image(golden_report, bot_username="TestBot")

    assert "<html" in img_html
    assert 'dir="rtl"' in img_html
    assert "شنبه" in img_html
    assert "چهارشنبه" in img_html
    # Image version must NOT include Thursday or Friday!
    assert "پنجشنبه" not in img_html
    assert "جمعه" not in img_html
    # Image version must NOT have 'آزاد' in empty cells
    assert "آزاد" not in img_html
    # Must have brand footer
    assert "@TestBot" in img_html


def test_html_color_classes(golden_report):
    renderer = HTMLRenderer()
    html_out = renderer.render_full(golden_report)
    for i in range(1, 10):
        assert f"c{i}" in html_out
