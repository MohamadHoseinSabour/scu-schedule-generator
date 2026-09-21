"""Admin authentication and authorization module."""

from __future__ import annotations

from typing import Optional
from fastapi import Header, HTTPException, status

from app.config.settings import get_settings


def verify_admin_key(x_admin_id: Optional[str] = Header(None)) -> int:
    """Verify that request contains an authorized Telegram Admin ID header."""
    settings = get_settings()

    if not x_admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin Telegram ID header (X-Admin-ID) missing",
        )

    try:
        admin_id = int(x_admin_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Admin ID format",
        )

    if admin_id not in settings.ADMIN_TELEGRAM_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Not an authorized administrator",
        )

    return admin_id
