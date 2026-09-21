from app.domain.models import ScheduleReport, ValidationResult, ConflictInfo

def validate_schedule(report: ScheduleReport) -> ValidationResult:
    errors = []
    warnings = []
    conflicts = []

    if not report.courses:
        errors.append("Schedule has no courses.")

    course_codes = set()
    for course in report.courses:
        if not course.code.isdigit():
            warnings.append(f"Course code '{course.code}' is not purely numeric.")
        if not course.title.strip():
            errors.append(f"Course '{course.code}' has empty title.")
        if course.units <= 0:
            errors.append(f"Course '{course.code}' has non-positive units: {course.units}")
        if course.code in course_codes:
            errors.append(f"Duplicate course code detected: {course.code}")
        course_codes.add(course.code)
        
        for session in course.sessions:
            if session.start_time >= session.end_time:
                errors.append(f"Course '{course.title}' session on {session.day} has start_time >= end_time.")

    # Conflict detection
    for i, c1 in enumerate(report.courses):
        for j, c2 in enumerate(report.courses):
            if i >= j: continue
            for s1 in c1.sessions:
                for s2 in c2.sessions:
                    if s1.day == s2.day:
                        if s1.start_time < s2.end_time and s2.start_time < s1.end_time:
                            overlap_start = max(s1.start_time, s2.start_time)
                            overlap_end = min(s1.end_time, s2.end_time)
                            conflicts.append(ConflictInfo(
                                course_a=c1.title,
                                course_b=c2.title,
                                day=s1.day.value,
                                overlap_start=overlap_start,
                                overlap_end=overlap_end
                            ))

    is_valid = len(errors) == 0 and len(conflicts) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings, conflicts=conflicts)
