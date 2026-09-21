---
name: docker-compose-patterns
description: Production-ready multi-service Docker configuration for Python FastAPI, Telegram bot, Celery worker, PostgreSQL, Redis, and Playwright Chromium dependencies.
---

# Docker Compose Patterns

This skill guides the containerization and service orchestration for the SCU Schedule Generator project.

## 1. Multi-Service Architecture
The stack consists of 5 coordinated services:
- `bot`: Telegram polling worker (`app.main`)
- `api`: FastAPI admin dashboard and health endpoints (`uvicorn app.admin.routes:app`)
- `worker`: Celery asynchronous queue worker for parsing & Playwright rendering
- `postgres`: Persistent relational storage (Port 5432)
- `redis`: In-memory broker & rate-limiter cache (Port 6379)

## 2. Playwright in Docker
When building the Docker image for Playwright on Debian/Ubuntu slim:
- Always install system browser dependencies:
  `RUN playwright install-deps chromium`
  `RUN playwright install chromium`
- Run as non-root user when possible or set appropriate sandbox permissions if running inside Docker containers (`--no-sandbox` flag).

## 3. Shared Volume for Generated Files
Persist generated files and temporary uploads across services using shared named volumes:
```yaml
volumes:
  storage_data:
```
Mounted to `/app/storage` in `bot`, `api`, and `worker`.
