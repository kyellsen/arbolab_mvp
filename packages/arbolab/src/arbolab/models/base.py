"""SQLAlchemy declarative base and shared mixins for ArboLab core models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for ArboLab SQLAlchemy models."""


class IdMixin:
    """Primary key mixin using an auto-incrementing integer identifier."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class TimestampMixin:
    """Timestamp mixin providing `created_at` and `updated_at` fields."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class DescribedMixin:
    """Optional naming and description fields for human-friendly records."""

    name: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)


class PropertiesMixin:
    """Extensibility fields for user-defined metadata and tags."""

    properties: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

