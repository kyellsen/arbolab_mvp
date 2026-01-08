"""SQLAlchemy declarative base and shared mixins for ArboLab core models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from sqlalchemy import JSON, DateTime, Integer, Sequence, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """Declarative base for ArboLab SQLAlchemy models."""

    def __repr__(self) -> str:
        """Machine-friendly string representation."""
        if hasattr(self, "id") and self.id is not None:
            identity = f"id={self.id}"
        else:
            identity = "transient"
        name = f" name={self.name!r}" if hasattr(self, "name") and self.name else ""
        return f"<{self.__class__.__name__} {identity}{name}>"

    def __str__(self) -> str:
        """User-friendly string representation."""
        if hasattr(self, "name") and self.name:
            return str(self.name)
        if hasattr(self, "id") and self.id:
            return f"{self.__class__.__name__} #{self.id}"
        return super().__str__()

    def to_dict(self) -> dict[str, Any]:
        """Export entity to dictionary."""
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }

    @classmethod
    def create(cls, session: Any, **kwargs: Any) -> Any:
        """Create and persist a new entity."""
        instance = cls(**kwargs)
        session.add(instance)
        # Flush to get ID and validate constraints immediately if needed, 
        # or let the user handle flushing. Active Record usually implies immediate-ish availability.
        # However, autoflush is usually on in SA sessions. We'll explicitly add.
        return instance

    @classmethod
    def get(cls, session: Any, ident: Any) -> Any | None:
        """Get an entity by primary key."""
        return session.get(cls, ident)

    def update(self, session: Any, **kwargs: Any) -> None:
        """Update entity fields."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.add(self)

    def delete(self, session: Any) -> None:
        """Delete entity."""
        session.delete(self)


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
