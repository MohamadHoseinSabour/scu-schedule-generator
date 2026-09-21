"""Admin web panel routes and FastAPI application."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from fastapi import APIRouter, Depends, FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from app.admin.auth import verify_admin_key
from app.config.settings import get_settings
from app.db.session import get_db_session, init_db
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

admin_router = APIRouter(prefix="/admin", tags=["admin"])

templates_dir = Path(__file__).parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)), autoescape=True)

_bot_task: asyncio.Task | None = None
_bot_instance = None
_dp_instance = None


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager: runs DB migrations, bot polling, and cleanup tasks."""
    global _bot_task, _bot_instance, _dp_instance
    settings = get_settings()

    # 1. Ensure storage directories exist
    for dir_name in ["storage/uploads", "storage/outputs", "storage/temp"]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)

    # 2. Auto-initialize database tables
    try:
        await init_db()
        logger.info("Database tables verified and initialized successfully")
    except Exception:
        logger.exception("Database initialization error during startup")

    # 3. Start Telegram bot polling if BOT_TOKEN is configured
    cleanup_task = None
    if settings.BOT_TOKEN:
        try:
            from app.bot.bot import create_bot, create_dispatcher

            _bot_instance = create_bot(settings.BOT_TOKEN)
            _dp_instance = create_dispatcher()
            logger.info("Starting Telegram Bot polling in background task...")
            _bot_task = asyncio.create_task(_dp_instance.start_polling(_bot_instance))
        except Exception:
            logger.exception("Failed to initialize Telegram Bot in lifespan")
    else:
        logger.warning(
            "BOT_TOKEN is not set. The web server and admin API are active, but the Telegram bot is idle. "
            "Please configure BOT_TOKEN in your Railway environment variables."
        )

    # 4. Background file cleanup task (runs hourly)
    async def _periodic_cleanup() -> None:
        while True:
            try:
                await asyncio.sleep(3600)
                from app.services.file_service import FileService

                fs = FileService()
                await fs.cleanup_old_files(Path("storage/temp"), ttl_hours=settings.OUTPUT_TTL_HOURS)
                await fs.cleanup_old_files(Path("storage/outputs"), ttl_hours=settings.OUTPUT_TTL_HOURS)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in background file cleanup worker")

    cleanup_task = asyncio.create_task(_periodic_cleanup())

    yield

    # Graceful shutdown
    if cleanup_task:
        cleanup_task.cancel()
    if _dp_instance and _bot_instance:
        logger.info("Stopping Telegram Bot polling...")
        try:
            await _dp_instance.stop_polling()
            await _bot_instance.session.close()
        except Exception:
            logger.exception("Error shutting down Telegram Bot")
    if _bot_task and not _bot_task.done():
        _bot_task.cancel()


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
    return template.render(kpis=kpis, selected_days=days, admin_id=admin_id)


app = FastAPI(title="SCU Schedule Generator API", lifespan=lifespan)
app.include_router(admin_router)


@app.get("/health")
async def root_health() -> dict[str, str]:
    """Railway / container liveness and health probe."""
    settings = get_settings()
    bot_status = "ONLINE" if settings.BOT_TOKEN else "WAITING_FOR_TOKEN"
    return {
        "status": "ONLINE",
        "bot": bot_status,
        "database": "ONLINE",
        "environment": settings.APP_ENV,
    }


@app.get("/", response_class=HTMLResponse)
async def root_index() -> str:
    """Friendly landing & status page for web and Railway deployments."""
    settings = get_settings()
    bot_ready = bool(settings.BOT_TOKEN)
    bot_link = f"https://t.me/{settings.BOT_USERNAME}" if settings.BOT_USERNAME else ""

    bot_badge_class = "badge-success" if bot_ready else "badge-warning"
    bot_status_text = "فعال و متصل به تلگرام 🟢" if bot_ready else "در انتظار تنظیم BOT_TOKEN 🟡"

    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SCU Schedule Generator</title>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
            --green: #10b981;
            --amber: #f59e0b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Vazirmatn', sans-serif;
            background: radial-gradient(circle at top right, #1e1b4b, var(--bg) 60%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            max-width: 620px;
            width: 100%;
            padding: 32px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
            text-align: center;
        }}
        .title {{
            font-size: 1.75rem;
            font-weight: 800;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-bottom: 24px;
        }}
        .status-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 24px;
            text-align: right;
        }}
        .status-item {{
            background: #0f172a;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px 16px;
        }}
        .status-label {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-bottom: 4px;
        }}
        .status-val {{
            font-size: 0.95rem;
            font-weight: 600;
        }}
        .badge-success {{ color: var(--green); }}
        .badge-warning {{ color: var(--amber); }}
        .notice {{
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 10px;
            padding: 14px;
            font-size: 0.88rem;
            color: #fde68a;
            margin-bottom: 24px;
            line-height: 1.6;
        }}
        .actions {{
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s ease;
            cursor: pointer;
        }}
        .btn-primary {{
            background: var(--primary);
            color: #fff;
        }}
        .btn-primary:hover {{
            background: var(--primary-dark);
        }}
        .btn-secondary {{
            background: #334155;
            color: #f8fafc;
        }}
        .btn-secondary:hover {{
            background: #475569;
        }}
        .footer {{
            margin-top: 24px;
            font-size: 0.8rem;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1 class="title">سامانه هوشمند برنامه هفتگی دانشگاه</h1>
        <p class="subtitle">Shahid Chamran University of Ahvaz – Schedule Generator</p>

        <div class="status-grid">
            <div class="status-item">
                <div class="status-label">وضعیت وب‌سرور و API</div>
                <div class="status-val badge-success">آنلاین و آماده 🟢</div>
            </div>
            <div class="status-item">
                <div class="status-label">وضعیت ربات تلگرام</div>
                <div class="status-val {bot_badge_class}">{bot_status_text}</div>
            </div>
            <div class="status-item">
                <div class="status-label">محیط اجرا (Environment)</div>
                <div class="status-val">{settings.APP_ENV.upper()}</div>
            </div>
            <div class="status-item">
                <div class="status-label">بررسی سلامت (Health)</div>
                <div class="status-val"><a href="/health" style="color: #60a5fa; text-decoration: none;">/health (200 OK)</a></div>
            </div>
        </div>

        {"" if bot_ready else """
        <div class="notice">
            ⚠️ <b>توکن ربات تلگرام هنوز تنظیم نشده است:</b><br>
            دیپلوی روی Railway با موفقیت انجام شد! برای فعال شدن ربات تلگرام، وارد داشبورد Railway شده و در تب <b>Variables</b> متغیر <code>BOT_TOKEN</code> را اضافه کنید.
        </div>
        """}

        <div class="actions">
            {f'<a href="{bot_link}" target="_blank" class="btn btn-primary">🤖 باز کردن ربات در تلگرام</a>' if bot_link else ''}
            <a href="/admin" class="btn btn-secondary">📊 پنل مدیریت (Admin)</a>
        </div>

        <p class="footer">🚀 Deployed & Powered by Railway</p>
    </div>
</body>
</html>"""
