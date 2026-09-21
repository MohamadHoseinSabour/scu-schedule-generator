from pydantic import BaseModel, Field
from datetime import time
from enum import Enum
from typing import Optional

class WeekDay(str, Enum):
    SATURDAY = 'شنبه'
    SUNDAY = 'یکشنبه'
    MONDAY = 'دوشنبه'
    TUESDAY = 'سهشنبه'
    WEDNESDAY = 'چهارشنبه'
    THURSDAY = 'پنجشنبه'
    FRIDAY = 'جمعه'

class CourseSession(BaseModel):
    day: WeekDay
    start_time: time
    end_time: time
    location: Optional[str] = None
    frequency: str = 'هر هفته'

class Course(BaseModel):
    code: str
    title: str
    group: Optional[str] = None
    units: float
    instructor: Optional[str] = None
    sessions: list[CourseSession]
    exam_date: Optional[str] = None
    exam_time: Optional[str] = None
    tuition: Optional[str] = None
    color_index: int = 0

class StudentInfo(BaseModel):
    name: Optional[str] = None
    student_id: Optional[str] = None
    faculty: Optional[str] = None
    major: Optional[str] = None
    degree: Optional[str] = None
    course_type: Optional[str] = None

class AcademicRecord(BaseModel):
    units_passed: Optional[str] = None
    units_taken: Optional[str] = None
    gpa: Optional[str] = None
    last_semester_avg: Optional[str] = None
    probation_count: Optional[str] = None

class ScheduleReport(BaseModel):
    semester: Optional[str] = None
    student: Optional[StudentInfo] = None
    academic_record: Optional[AcademicRecord] = None
    courses: list[Course]
    report_date: Optional[str] = None

    @property
    def total_courses(self) -> int:
        return len(self.courses)

    @property
    def total_units(self) -> float:
        return sum(course.units for course in self.courses)

    @property
    def has_conflicts(self) -> bool:
        # Avoid circular import, simple conflict check based on overlap can be here or rely on validation
        for i, c1 in enumerate(self.courses):
            for j, c2 in enumerate(self.courses):
                if i >= j: continue
                for s1 in c1.sessions:
                    for s2 in c2.sessions:
                        if s1.day == s2.day:
                            if s1.start_time < s2.end_time and s2.start_time < s1.end_time:
                                return True
        return False

class ConflictInfo(BaseModel):
    course_a: str
    course_b: str
    day: str
    overlap_start: time
    overlap_end: time

class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    conflicts: list[ConflictInfo]
