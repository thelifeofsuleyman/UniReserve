"""Normalized UniReserve tables (design diagram 05-erd-logical-3nf)."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    __table_args__ = (CheckConstraint("role IN ('STUDENT','STAFF','ADMIN')", name="ck_role"),)

class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    __table_args__ = (CheckConstraint("category IN ('ROOM','EQUIPMENT')", name="ck_resource_category"),)

class Reservation(Base):
    __tablename__ = "reservations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="RESTRICT"), nullable=False)
    # SQLite persists UTC-naive datetime values. Service boundaries convert to/from aware UTC.
    start_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    created_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    __table_args__ = (
        CheckConstraint("start_utc < end_utc", name="ck_time_order"),
        CheckConstraint("status IN ('PENDING_APPROVAL','CONFIRMED','REJECTED','CANCELLED')", name="ck_reservation_status"),
        Index("ix_confirmed_resource_window", "resource_id", "status", "start_utc", "end_utc"),
        Index("ix_reservation_owner", "user_id"),
    )

class ReservationEvent(Base):
    __tablename__ = "reservation_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id", ondelete="RESTRICT"), nullable=False)
    actor_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    previous_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    occurred_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    __table_args__ = (Index("ix_event_reservation", "reservation_id"),)
