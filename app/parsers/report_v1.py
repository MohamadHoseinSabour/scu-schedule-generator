from typing import Any
from datetime import datetime, time
from app.parsers.base import ReportParser
from app.domain.models import (
    ScheduleReport, Course, CourseSession, WeekDay, StudentInfo, AcademicRecord
)
from app.parsers.normalizer import Normalizer

class ReportV1Parser(ReportParser):
    def can_parse(self, workbook: Any) -> bool:
        if workbook.nsheets == 0:
            return False
        sheet = workbook.sheet_by_index(0)
        
        # Check if row 14 col 0 contains 'برنامه هفتگی دانشجو' or row 0 col 14 contains 'دانشگاه شهید چمران'
        try:
            val_14_0 = str(sheet.cell_value(14, 0))
            if 'برنامه هفتگی دانشجو' in val_14_0:
                return True
        except IndexError:
            pass
            
        try:
            val_0_14 = str(sheet.cell_value(0, 14))
            if 'دانشگاه شهید چمران' in val_0_14:
                return True
        except IndexError:
            pass
            
        return False

    def parse(self, workbook: Any) -> ScheduleReport:
        sheet = workbook.sheet_by_index(0)
        
        # Extract Student Info
        student = StudentInfo(
            name=self._safe_get_cell(sheet, 6, 25),
            student_id=Normalizer.normalize_digits(self._safe_get_cell(sheet, 8, 25)),
            faculty=self._safe_get_cell(sheet, 8, 18),
            major=self._safe_get_cell(sheet, 11, 18),
            degree=self._safe_get_cell(sheet, 11, 7),
            course_type=self._safe_get_cell(sheet, 11, 25)
        )
        semester = self._safe_get_cell(sheet, 6, 18)

        # Extract Academic Record
        record = AcademicRecord(
            units_passed=Normalizer.normalize_digits(self._safe_get_cell(sheet, 43, 23)),
            units_taken=Normalizer.normalize_digits(self._safe_get_cell(sheet, 43, 27)),
            gpa=Normalizer.normalize_digits(self._safe_get_cell(sheet, 43, 38)),
            last_semester_avg=Normalizer.normalize_digits(self._safe_get_cell(sheet, 43, 41)),
            probation_count=Normalizer.normalize_digits(self._safe_get_cell(sheet, 43, 32))
        )

        courses = []
        data_rows = [16, 18, 20, 22, 24, 26, 28, 30, 32]
        color_index = 1
        
        for row_idx in data_rows:
            code = Normalizer.normalize_digits(self._safe_get_cell(sheet, row_idx, 42))
            if not code:
                continue
                
            title = Normalizer.clean_text(self._safe_get_cell(sheet, row_idx, 30))
            group = Normalizer.normalize_digits(self._safe_get_cell(sheet, row_idx, 39))
            units_str = Normalizer.normalize_digits(self._safe_get_cell(sheet, row_idx, 28))
            units = float(units_str) if units_str else 0.0
            
            instructor = Normalizer.clean_text(self._safe_get_cell(sheet, row_idx, 4))
            tuition = Normalizer.normalize_digits(self._safe_get_cell(sheet, row_idx, 0))
            exam_date = Normalizer.normalize_digits(self._safe_get_cell(sheet, row_idx, 12))
            exam_time = Normalizer.normalize_digits(self._safe_get_cell(sheet, row_idx, 10))
            
            schedule_raw = self._safe_get_cell(sheet, row_idx, 16)
            sessions = self._parse_schedule(schedule_raw)
            
            courses.append(Course(
                code=code,
                title=title,
                group=group,
                units=units,
                instructor=instructor,
                sessions=sessions,
                exam_date=exam_date,
                exam_time=exam_time,
                tuition=tuition,
                color_index=color_index
            ))
            color_index += 1

        return ScheduleReport(
            semester=semester,
            student=student,
            academic_record=record,
            courses=courses
        )

    def _safe_get_cell(self, sheet: Any, row: int, col: int) -> str:
        try:
            val = sheet.cell_value(row, col)
            if isinstance(val, float):
                # Check if it's an integer stored as float
                if val.is_integer():
                    return str(int(val))
            return str(val).strip()
        except IndexError:
            return ""

    def _parse_schedule(self, schedule_raw: str) -> list[CourseSession]:
        sessions = []
        if not schedule_raw:
            return sessions
            
        # Split by \n، or \n,
        parts = schedule_raw.replace('\\n', '\n').split('\n')
        subparts = []
        for p in parts:
            p = p.strip()
            if p.startswith('،') or p.startswith(','):
                p = p[1:].strip()
            if p:
                # Sometimes it splits on multiple lines with ، at the end
                for sp in p.split('،'):
                    sp = sp.strip()
                    if sp:
                        subparts.append(sp)

        for session_str in subparts:
            # e.g., ی-14:00-15:30-مهندسی_کلاس 219-هر هفته
            session_parts = session_str.split('-')
            if len(session_parts) >= 5:
                day_abbrev = session_parts[0].strip()
                start_str = session_parts[1].strip()
                end_str = session_parts[2].strip()
                
                # location might have - in it
                location = "-".join(session_parts[3:-1]).strip()
                location = location.replace('_', ' ')
                frequency = session_parts[-1].strip()
                
                day_name = Normalizer.normalize_day(day_abbrev)
                start_time_str = Normalizer.normalize_time(start_str)
                end_time_str = Normalizer.normalize_time(end_str)
                
                start_h, start_m = map(int, start_time_str.split(':'))
                end_h, end_m = map(int, end_time_str.split(':'))
                
                sessions.append(CourseSession(
                    day=WeekDay(day_name),
                    start_time=time(start_h, start_m),
                    end_time=time(end_h, end_m),
                    location=location,
                    frequency=frequency
                ))
        return sessions
