"""HTML Renderer module.

Transforms a ScheduleReport into complete self-contained HTML strings
using Jinja2 templates. Supports two rendering modes:
  - Full interactive HTML (with buttons, notes, LocalStorage)
  - Image-only HTML (clean, for Playwright screenshot)
"""

from __future__ import annotations

import os
from datetime import time
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.domain.models import Course, CourseSession, ScheduleReport, WeekDay

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Ordered list of display days for the full HTML (Sat → Fri)
FULL_DAYS: list[WeekDay] = [
    WeekDay.SATURDAY,
    WeekDay.SUNDAY,
    WeekDay.MONDAY,
    WeekDay.TUESDAY,
    WeekDay.WEDNESDAY,
    WeekDay.THURSDAY,
    WeekDay.FRIDAY,
]

#: Ordered list of display days for the image export (Sat → Wed only)
IMAGE_DAYS: list[WeekDay] = [
    WeekDay.SATURDAY,
    WeekDay.SUNDAY,
    WeekDay.MONDAY,
    WeekDay.TUESDAY,
    WeekDay.WEDNESDAY,
]

#: Default time‑slot boundaries (start_hour, end_hour)
DEFAULT_TIME_SLOTS: list[tuple[int, int]] = [
    (8, 10),
    (10, 12),
    (12, 14),
    (14, 16),
    (16, 18),
]


# ---------------------------------------------------------------------------
# Jinja2 filter helpers
# ---------------------------------------------------------------------------

_PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"


def to_persian(value: int | float | str) -> str:
    """Convert ASCII digits in *value* to Persian digits."""
    text = str(value)
    return text.translate(str.maketrans("0123456789", _PERSIAN_DIGITS))


def format_time_persian(t: time) -> str:
    """Format a :class:`~datetime.time` as ``۱۴:۰۰``."""
    return to_persian(t.strftime("%H:%M"))


# ---------------------------------------------------------------------------
# Grid builder
# ---------------------------------------------------------------------------

class SlotInfo:
    """Represents one cell in the schedule grid."""

    def __init__(
        self,
        course: Course | None = None,
        session: CourseSession | None = None,
    ) -> None:
        self.course = course
        self.session = session

    @property
    def time_display(self) -> str:
        if self.session is None:
            return ""
        return (
            f"{format_time_persian(self.session.start_time)}"
            f"–{format_time_persian(self.session.end_time)}"
        )

    @property
    def location_display(self) -> str:
        if self.session is None or not self.session.location:
            return ""
        return self.session.location


class DayRow:
    """One row (day) in the schedule grid."""

    def __init__(self, day: WeekDay, slots: list[SlotInfo]) -> None:
        self.name: str = day.value
        self.day: WeekDay = day
        self.slots: list[SlotInfo] = slots
        self.is_holiday: bool = day in (WeekDay.THURSDAY, WeekDay.FRIDAY)


def _slot_index_for_session(session: CourseSession) -> int | None:
    """Return the 0‑based slot index a session's *start_time* falls into."""
    start_hour = session.start_time.hour
    for idx, (sh, eh) in enumerate(DEFAULT_TIME_SLOTS):
        if sh <= start_hour < eh:
            return idx
    return None


def build_schedule_grid(
    report: ScheduleReport,
    days: list[WeekDay] | None = None,
) -> list[DayRow]:
    """Build a grid mapping each ``(day, time_slot)`` to a :class:`SlotInfo`.

    Parameters
    ----------
    report:
        The canonical schedule report to lay out.
    days:
        Which days to include.  Defaults to :data:`FULL_DAYS`.
    """
    if days is None:
        days = FULL_DAYS

    num_slots = len(DEFAULT_TIME_SLOTS)
    rows: list[DayRow] = []

    for day in days:
        slots = [SlotInfo() for _ in range(num_slots)]

        for course in report.courses:
            for session in course.sessions:
                if session.day == day:
                    idx = _slot_index_for_session(session)
                    if idx is not None:
                        slots[idx] = SlotInfo(course=course, session=session)

        rows.append(DayRow(day=day, slots=slots))

    return rows


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

class HTMLRenderer:
    """Renders :class:`ScheduleReport` objects into HTML strings."""

    def __init__(self, template_dir: str | Path | None = None) -> None:
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
        self._template_dir = Path(template_dir)
        self._env = Environment(
            loader=FileSystemLoader(str(self._template_dir)),
            autoescape=select_autoescape(["html"]),
        )
        # Register custom filters
        self._env.filters["to_persian"] = to_persian
        self._env.filters["format_time_persian"] = format_time_persian

    # -- public API ---------------------------------------------------------

    def render_full(self, report: ScheduleReport) -> str:
        """Render the full interactive HTML schedule.

        Includes Thursday/Friday, buttons, notes, LocalStorage JS.
        """
        grid = build_schedule_grid(report, days=FULL_DAYS)
        status_text = self._get_status_text(report)

        template = self._env.get_template("weekly_schedule.html")
        return template.render(
            report=report,
            schedule_grid=grid,
            courses=report.courses,
            total_courses_persian=to_persian(report.total_courses),
            total_units_persian=to_persian(int(report.total_units)),
            status_text=status_text,
            time_slots=DEFAULT_TIME_SLOTS,
            to_persian=to_persian,
            format_time_persian=format_time_persian,
        )

    def render_image(
        self,
        report: ScheduleReport,
        bot_username: str = "",
    ) -> str:
        """Render a clean image‑only HTML (no Thursday/Friday, no buttons).

        Designed to be screenshotted by Playwright.
        """
        grid = build_schedule_grid(report, days=IMAGE_DAYS)
        status_text = self._get_status_text(report)

        template = self._env.get_template("schedule_image.html")
        return template.render(
            report=report,
            schedule_grid=grid,
            courses=report.courses,
            total_courses_persian=to_persian(report.total_courses),
            total_units_persian=to_persian(int(report.total_units)),
            status_text=status_text,
            time_slots=DEFAULT_TIME_SLOTS,
            bot_username=bot_username,
            to_persian=to_persian,
            format_time_persian=format_time_persian,
        )

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _get_status_text(report: ScheduleReport) -> str:
        if report.has_conflicts:
            return "⚠️ دارای تداخل زمانی"
        return "برنامه بدون تداخل"
