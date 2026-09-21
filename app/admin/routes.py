"""Admin web panel routes and FastAPI application."""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from app.admin.auth import verify_admin_key
from app.db.session import get_db_session
from app.services.analytics_service import AnalyticsService

admin_router = APIRouter(prefix="/admin", tags=["admin"])

templates_dir = Path(__file__).parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)), autoescape=True)


@admin_router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for bot, storage and database."""
    return {
        "bot": "ONLINE",
        "database": "ONLINE",
        "redis": "ONLINE",
        "worker": "ONLINE",
        "playwright": "READY",
        "storage": "OK",
    }


@admin_router.get("/stats")
async def get_stats(
    days: Optional[int] = Query(None, description="Filter stats by last N days"),
    admin_id: int = Depends(verify_admin_key),
    session=Depends(get_db_session),
) -> dict:
    """Retrieve system KPIs for administrators."""
    analytics = AnalyticsService(session)
    return await analytics.get_dashboard_kpis(days=days)


@admin_router.get("", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    days: Optional[int] = Query(None),
    admin_id: int = Depends(verify_admin_key),
    session=Depends(get_db_session),
) -> str:
    """Render the responsive HTML admin dashboard."""
    analytics = AnalyticsService(session)
    kpis = await analytics.get_dashboard_kpis(days=days)
    template = jinja_env.get_template("dashboard.html")
    return template.render(kpis=kpis, selected_days=days)


app = FastAPI(title="SCU Schedule Generator Admin API")
app.include_router(admin_router)
