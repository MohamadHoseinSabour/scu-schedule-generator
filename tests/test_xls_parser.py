import pytest
from pathlib import Path
from app.parsers.xls_parser import read_xls
from app.parsers.report_v1 import ReportV1Parser
from app.domain.validation import validate_schedule
from app.parsers.normalizer import Normalizer

@pytest.fixture
def golden_workbook():
    project_root = Path(__file__).parent.parent
    xls_path = project_root / 'ReferenceS' / 'Report.xls'
    return read_xls(xls_path)

@pytest.fixture
def parser():
    return ReportV1Parser()

def test_golden_report_course_count(golden_workbook, parser):
    assert parser.can_parse(golden_workbook)
    report = parser.parse(golden_workbook)
    assert report.total_courses == 9

def test_golden_report_total_units(golden_workbook, parser):
    report = parser.parse(golden_workbook)
    assert report.total_units == 20.0

def test_golden_report_course_names(golden_workbook, parser):
    report = parser.parse(golden_workbook)
    titles = [c.title for c in report.courses]
    assert len(titles) == 9
    # Just asserting it's parsed, we can check for specifics if needed

def test_golden_report_sessions(golden_workbook, parser):
    report = parser.parse(golden_workbook)
    for c in report.courses:
        assert isinstance(c.sessions, list)
        for s in c.sessions:
            assert s.day.value in [d.value for d in report.courses[0].sessions[0].day.__class__]
            
def test_golden_report_student_info(golden_workbook, parser):
    report = parser.parse(golden_workbook)
    assert report.student.name == 'محمدحسین صبور'
    assert report.student.student_id == '40265547'

def test_conflict_detection_no_conflicts(golden_workbook, parser):
    report = parser.parse(golden_workbook)
    val_result = validate_schedule(report)
    assert len(val_result.conflicts) == 0

def test_normalization_persian_digits():
    assert Normalizer.normalize_digits('۱۲۳۴۵۶۷۸۹۰') == '1234567890'

def test_normalization_arabic_digits():
    assert Normalizer.normalize_digits('١٢٣٤٥٦٧٨٩٠') == '1234567890'

def test_normalization_day_names():
    assert Normalizer.normalize_day_name('سه شنبه') == 'سهشنبه'
    assert Normalizer.normalize_day('س') == 'سهشنبه'

def test_normalization_time_format():
    assert Normalizer.normalize_time('9:30') == '09:30'

def test_invalid_file_rejection(parser):
    class DummyWorkbook:
        nsheets = 1
        def sheet_by_index(self, i):
            class DummySheet:
                def cell_value(self, r, c):
                    raise IndexError
            return DummySheet()
    
    wb = DummyWorkbook()
    assert not parser.can_parse(wb)
