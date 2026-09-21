"""Admin authentication and authorization module."""

from __future__ import annotations

from typing import Optional
from fastapi import Header, HTTPException, Query, status

from app.config.settings import get_settings


def verify_admin_key(
    x_admin_id: Optional[str] = Header(None),
    admin_id_query: Optional[str] = Query(None, alias="admin_id"),
) -> int:
    """Verify that request contains an authorized Telegram Admin ID (via Header or Query Param)."""
    settings = get_settings()
    raw_id = x_admin_id or admin_id_query

    if not raw_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="شناسه ادمین تلگرام ارسال نشده است (هدر X-Admin-ID یا پارامتر ?admin_id= لازم است)",
        )

    try:
        admin_id = int(raw_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فرمت شناسه ادمین نامعتبر است (باید عدد باشد)",
        )

    if admin_id not in settings.ADMIN_TELEGRAM_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی غیرمجاز: این شناسه در لیست ادمین‌ها (ADMIN_TELEGRAM_IDS) ثبت نشده است",
        )

    return admin_id
