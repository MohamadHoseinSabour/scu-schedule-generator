"""Shahid Chamran University of Ahvaz (SCU) Portal Adapter Stub."""

from __future__ import annotations

import logging
from pathlib import Path

from app.config.feature_flags import get_feature_flags
from app.integrations.portal.base import PortalSession, UniversityPortalAdapter

logger = logging.getLogger(__name__)


class SCUPortalAdapter(UniversityPortalAdapter):
    """Adapter for the SCU Sama/Golestan academic portal."""

    def __init__(self, base_url: str = "https://sama.scu.ac.ir") -> None:
        self.base_url = base_url

    async def login(self, username: str, password: str) -> PortalSession:
        """Authenticate user against SCU portal."""
        flags = get_feature_flags()
        if not flags.PORTAL_ENABLED:
            raise NotImplementedError("University portal integration is currently disabled (PORTAL_ENABLED=false)")

        # IMPORTANT: Real browser automation selectors must be extracted from the target portal.
        # NEVER log the password.
        logger.info("Attempting portal login for student %s", username)
        raise NotImplementedError("SCU portal live selectors pending field inspection.")

    async def download_report(self, session: PortalSession, target_dir: Path) -> Path:
        """Download student course schedule report."""
        flags = get_feature_flags()
        if not flags.PORTAL_ENABLED:
            raise NotImplementedError("University portal integration is currently disabled (PORTAL_ENABLED=false)")

        raise NotImplementedError("Report download automation pending portal selector mapping.")

    async def logout(self, session: PortalSession) -> None:
        """Log out and terminate browser session."""
        logger.info("Terminating portal session for student %s", session.student_id)
