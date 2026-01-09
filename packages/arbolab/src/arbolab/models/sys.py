"""System-level internal metadata models."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from arbolab.models.base import Base


class SysMetadata(Base):
    """Internal key-value store for system metadata (e.g., catalog versions)."""

    __tablename__ = "core_sys_metadata"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String, nullable=False)
