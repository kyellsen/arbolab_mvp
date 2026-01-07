"""Pydantic base models for ArboLab schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ArboLabSchema(BaseModel):
    """Base class for Pydantic schemas with ORM support."""

    model_config = ConfigDict(from_attributes=True)


class EntitySchema(ArboLabSchema):
    """Common fields for persisted domain entities."""

    id: int
    created_at: datetime
    updated_at: datetime
    name: str | None = None
    description: str | None = None
    properties: dict[str, Any] | None = None
    tags: list[str] | None = None
