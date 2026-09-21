"""Base interface for University Portal Adapters (Phase 2 Architecture)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PortalSession:
    """Represents an active authenticated portal session."""
    session_id: str
    cookies: dict[str, str]
    student_id: str
    is_authenticated: bool = True


class UniversityPortalAdapter(ABC):
    """Abstract interface defining the contract for university portal scraping."""

    @abstractmethod
    async def login(self, username: str, password: str) -> PortalSession:
        """Authenticate with the academic portal.

        SECURITY REQUIREMENT: Passwords must only be processed in memory and never logged or persisted.
        """
        pass

    @abstractmethod
    async def download_report(self, session: PortalSession, target_dir: Path) -> Path:
        """Navigate to student enrollment verification and download the Excel report."""
        pass

    @abstractmethod
    async def logout(self, session: PortalSession) -> None:
        """Terminate the academic portal session."""
        pass
