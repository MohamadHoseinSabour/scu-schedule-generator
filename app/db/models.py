"""SQLAlchemy ORM models for database persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    """Telegram user profile and referral tracking."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    referral_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    referred_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    share_events: Mapped[list["ShareEvent"]] = relationship("ShareEvent", back_populates="user", cascade="all, delete-orphan")


class Job(Base):
    """File processing conversion jobs."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # JOB-YYYYMMDD-XXXXX
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)  # pending, success, failed
    source_type: Mapped[str] = mapped_column(String(32), default="upload", nullable=False)  # upload, portal
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # xls, xlsx
    started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    processing_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="jobs")
    uploaded_file: Mapped[Optional["UploadedFile"]] = relationship("UploadedFile", back_populates="job", uselist=False, cascade="all, delete-orphan")
    generated_output: Mapped[Optional["GeneratedOutput"]] = relationship("GeneratedOutput", back_populates="job", uselist=False, cascade="all, delete-orphan")


class UploadedFile(Base):
    """Details of uploaded source files."""

    __tablename__ = "uploaded_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(64), ForeignKey("jobs.id"), unique=True, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    extension: Mapped[str] = mapped_column(String(16), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="uploaded_file")


class GeneratedOutput(Base):
    """Details and paths of generated outputs."""

    __tablename__ = "generated_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(64), ForeignKey("jobs.id"), unique=True, nullable=False)
    html_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    image_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    html_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="generated_output")


class ShareEvent(Base):
    """Tracking share button clicks."""

    __tablename__ = "share_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(32), default="share_click", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="share_events")


class Referral(Base):
    """Successful referral joins tracking."""

    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    referrer_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    referred_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)


class PortalAttempt(Base):
    """Portal login attempts (Phase 2 audit - NEVER stores credentials)."""

    __tablename__ = "portal_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # initiated, success, failed
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
