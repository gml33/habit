from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_id"),
        UniqueConstraint("api_token", name="uq_user_api_token"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    timezone: Mapped[str] = mapped_column(
        String, nullable=False, default="America/Argentina/Buenos_Aires"
    )
    api_token: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class Checkin(Base):
    __tablename__ = "checkins"
    __table_args__ = (UniqueConstraint("user_id", "ts_hour_utc", name="uq_user_ts_hour_utc"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.user_id"), nullable=False, index=True
    )
    ts_hour_utc: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    activity: Mapped[str] = mapped_column(String, nullable=False)
    emotion: Mapped[str] = mapped_column(String, nullable=False)
    energy: Mapped[str] = mapped_column(String, nullable=False)
    stress: Mapped[str] = mapped_column(String, nullable=False)
    note: Mapped[str | None] = mapped_column(String(140), nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
