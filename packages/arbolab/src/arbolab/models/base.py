"""SQLAlchemy declarative base and shared mixins for ArboLab core models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from sqlalchemy import JSON, DateTime, Integer, Sequence, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """Declarative base for ArboLab SQLAlchemy models."""


class _HasTableName(Protocol):
    """Protocol for declarative classes that define `__tablename__`."""

    __tablename__: str


class IdMixin:
    """Primary key mixin using an auto-incrementing integer identifier."""

    @declared_attr.directive
    def id(cls: type[_HasTableName]) -> Mapped[int]:
        """Primary key with a per-table sequence server default."""

        sequence = Sequence(f"{cls.__tablename__}_id_seq")
        return mapped_column(
            Integer,
            sequence,
            primary_key=True,
            server_default=sequence.next_value(),
        )


class TimestampMixin:
    """Timestamp mixin providing `created_at` and `updated_at` fields."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
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
