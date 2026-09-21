"""Tests for Admin API endpoints and security controls."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.admin.routes import app
from app.config.settings import get_settings


@pytest.mark.asyncio
async def test_admin_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/admin/health")
        assert response.status_code == 200
        data = response.json()
        assert data["bot"] == "ONLINE"
        assert data["playwright"] == "READY"


@pytest.mark.asyncio
async def test_root_health_and_landing():
    """Verify Railway root health check and landing page endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test Railway health probe
        health_resp = await client.get("/health")
        assert health_resp.status_code == 200
        health_data = health_resp.json()
        assert health_data["status"] == "ONLINE"
        assert "bot" in health_data
        assert "database" in health_data

        # Test root landing page
        index_resp = await client.get("/")
        assert index_resp.status_code == 200
        assert "SCU Schedule Generator" in index_resp.text
        assert "Railway" in index_resp.text


@pytest.mark.asyncio
async def test_admin_stats_unauthorized():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Request with missing header
        response = await client.get("/admin/stats")
        assert response.status_code == 401

        # Request with unauthorized ID
        response_forbidden = await client.get(
            "/admin/stats",
            headers={"X-Admin-ID": "999999999"}
        )
        assert response_forbidden.status_code == 403


from app.db.session import init_db


@pytest.mark.asyncio
async def test_admin_stats_authorized():
    await init_db()
    settings = get_settings()
    # Add a mock admin ID to settings for test
    admin_id = 123456789
    settings.ADMIN_TELEGRAM_IDS.append(admin_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/admin/stats",
            headers={"X-Admin-ID": str(admin_id)}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_jobs" in data
