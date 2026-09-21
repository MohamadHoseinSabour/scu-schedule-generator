"""Analytics and telemetry tracking service."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import GeneratedOutput, Job, Referral, ShareEvent, User


class AnalyticsService:
    """Provides methods to track lifecycle events and query dashboard KPIs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_dashboard_kpis(self, days: Optional[int] = None) -> dict[str, Any]:
        """Aggregate KPIs for admin dashboard."""
        since: Optional[datetime] = None
        if days is not None:
            since = datetime.utcnow() - timedelta(days=days)

        # 1. Total users
        user_stmt = select(func.count(User.id))
        if since:
            user_stmt = user_stmt.where(User.created_at >= since)
        total_users = (await self.session.execute(user_stmt)).scalar_one()

        # 2. Total received files (jobs)
        job_stmt = select(func.count(Job.id))
        if since:
            job_stmt = job_stmt.where(Job.started_at >= since)
        total_jobs = (await self.session.execute(job_stmt)).scalar_one()

        # 3. Successful conversions
        success_stmt = select(func.count(Job.id)).where(Job.status == "success")
        if since:
            success_stmt = success_stmt.where(Job.started_at >= since)
        successful_conversions = (await self.session.execute(success_stmt)).scalar_one()

        # 4. Failed conversions
        failed_stmt = select(func.count(Job.id)).where(Job.status == "failed")
        if since:
            failed_stmt = failed_stmt.where(Job.started_at >= since)
        failed_conversions = (await self.session.execute(failed_stmt)).scalar_one()

        # 5. Generated HTML count
        html_stmt = select(func.count(GeneratedOutput.id)).where(GeneratedOutput.html_generated.is_(True))
        if since:
            html_stmt = html_stmt.where(GeneratedOutput.created_at >= since)
        total_html = (await self.session.execute(html_stmt)).scalar_one()

        # 6. Generated Images count
        img_stmt = select(func.count(GeneratedOutput.id)).where(GeneratedOutput.image_generated.is_(True))
        if since:
            img_stmt = img_stmt.where(GeneratedOutput.created_at >= since)
        total_images = (await self.session.execute(img_stmt)).scalar_one()

        # 7. Share clicks
        share_stmt = select(func.count(ShareEvent.id))
        if since:
            share_stmt = share_stmt.where(ShareEvent.created_at >= since)
        share_clicks = (await self.session.execute(share_stmt)).scalar_one()

        # 8. Referrals count
        ref_stmt = select(func.count(Referral.id))
        if since:
            ref_stmt = ref_stmt.where(Referral.created_at >= since)
        referral_count = (await self.session.execute(ref_stmt)).scalar_one()

        # 9. Average processing time
        avg_time_stmt = select(func.avg(Job.processing_time)).where(Job.status == "success")
        if since:
            avg_time_stmt = avg_time_stmt.where(Job.started_at >= since)
        avg_time = (await self.session.execute(avg_time_stmt)).scalar_one() or 0.0

        return {
            "total_users": total_users,
            "total_jobs": total_jobs,
            "successful_conversions": successful_conversions,
            "failed_conversions": failed_conversions,
            "total_html": total_html,
            "total_images": total_images,
            "share_clicks": share_clicks,
            "referral_count": referral_count,
            "avg_processing_time": round(float(avg_time), 2),
        }
