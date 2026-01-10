from sqlalchemy import DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    password_salt: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )


class Checkin(Base):
    __tablename__ = "checkins"
    __table_args__ = (UniqueConstraint("user_id", "ts_hour", name="uq_user_ts_hour"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    ts_hour: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    activity: Mapped[str] = mapped_column(String, nullable=False)
    emotion: Mapped[str] = mapped_column(String, nullable=False)
    energy: Mapped[str] = mapped_column(String, nullable=False)
    stress: Mapped[str] = mapped_column(String, nullable=False)
    note: Mapped[str | None] = mapped_column(String(140), nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
