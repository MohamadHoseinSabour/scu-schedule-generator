"""Pytest configuration and shared test fixtures."""

from datetime import time
from pathlib import Path
import pytest

from app.config.feature_flags import FeatureFlags
from app.config.settings import Settings
from app.domain.models import (
    AcademicRecord,
    Course,
    CourseSession,
    ScheduleReport,
    StudentInfo,
    WeekDay,
)
from app.db.session import Base, set_engine
from sqlalchemy.ext.asyncio import create_async_engine


import asyncio


@pytest.fixture(autouse=True)
def isolate_database_for_tests(tmp_path: Path):
    """Ensure tests run against an isolated temporary SQLite database."""
    test_db_file = tmp_path / "test_suite.db"
    test_engine = create_async_engine(f"sqlite+aiosqlite:///{test_db_file}", echo=False)
    set_engine(test_engine)

    async def _init_db():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_init_db())
    yield

    async def _dispose_db():
        await test_engine.dispose()

    asyncio.run(_dispose_db())
    set_engine(None)


@pytest.fixture
def project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def sample_excel_path(project_root: Path) -> Path:
    """Return the path to the reference Report.xls file."""
    return project_root / "ReferenceS" / "Report.xls"


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    """Return test settings with temporary storage and test flags."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return Settings(
        BOT_TOKEN="123456:TEST_BOT_TOKEN_MOCK",
        BOT_USERNAME="test_scu_bot",
        ADMIN_TELEGRAM_IDS=[123456789],
        DATABASE_URL=f"sqlite+aiosqlite:///{storage_dir}/test.db",
        STORAGE_PATH=str(storage_dir),
        APP_ENV="test",
        PARSER_DEBUG=True,
    )


@pytest.fixture
def test_feature_flags() -> FeatureFlags:
    """Return test feature flags with all capabilities enabled."""
    return FeatureFlags(
        PORTAL_ENABLED=True,
        ADMIN_ENABLED=True,
        REFERRAL_ENABLED=True,
        IMAGE_EXPORT_ENABLED=True,
        HTML_EXPORT_ENABLED=True,
    )


@pytest.fixture
def temp_storage_dirs(tmp_path: Path) -> dict[str, Path]:
    """Create and return temporary directories for storage tests."""
    dirs = {
        "uploads": tmp_path / "storage" / "uploads",
        "outputs": tmp_path / "storage" / "outputs",
        "temp": tmp_path / "storage" / "temp",
    }
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)
    return dirs


@pytest.fixture
def sample_session_saturday() -> CourseSession:
    """Return a sample CourseSession on Saturday."""
    return CourseSession(
        day=WeekDay.SATURDAY,
        start_time=time(8, 0),
        end_time=time(10, 0),
        location="کلاس ۱۰۱",
        frequency="هر هفته",
    )


@pytest.fixture
def sample_session_monday() -> CourseSession:
    """Return a sample CourseSession on Monday."""
    return CourseSession(
        day=WeekDay.MONDAY,
        start_time=time(10, 0),
        end_time=time(12, 0),
        location="کلاس ۱۰۲",
        frequency="هر هفته",
    )


@pytest.fixture
def sample_course(sample_session_saturday: CourseSession) -> Course:
    """Return a sample Course instance."""
    return Course(
        code="1234567",
        title="مبانی کامپیوتر و برنامه‌نویسی",
        group="01",
        units=3.0,
        instructor="دکتر رضایی",
        sessions=[sample_session_saturday],
        exam_date="1403/03/20",
        exam_time="09:00",
        tuition="0",
        color_index=1,
    )


@pytest.fixture
def sample_student_info() -> StudentInfo:
    """Return sample student information."""
    return StudentInfo(
        name="محمدحسین صبور",
        student_id="9912345678",
        faculty="مهندسی",
        major="مهندسی کامپیوتر",
        degree="کارشناسی",
        course_type="روزانه",
    )


@pytest.fixture
def sample_academic_record() -> AcademicRecord:
    """Return sample academic record information."""
    return AcademicRecord(
        units_passed="80",
        units_taken="20",
        gpa="17.50",
        last_semester_avg="18.20",
        probation_count="0",
    )


@pytest.fixture
def sample_schedule_report(
    sample_student_info: StudentInfo,
    sample_academic_record: AcademicRecord,
    sample_course: Course,
) -> ScheduleReport:
    """Return a sample ScheduleReport instance with one course."""
    return ScheduleReport(
        semester="نیمسال دوم 1402-1403",
        student=sample_student_info,
        academic_record=sample_academic_record,
        courses=[sample_course],
        report_date="1403/01/15",
    )
