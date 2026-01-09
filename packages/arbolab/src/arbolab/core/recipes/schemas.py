from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class RecipeStep(BaseModel):
    """A single reproducible operation in the Lab."""
    step_id: str = Field(..., description="Unique identifier for the step (e.g. UUID)")
    step_type: str = Field(..., description="The type of operation (e.g. define_project)")
    params: dict[str, Any] = Field(default_factory=dict, description="Parameters for the operation")
    author_id: str | None = Field(None, description="The user who initiated the step")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the step was recorded")

class Recipe(BaseModel):
    """A collection of steps representing a reproducible experiment or lab state."""
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    steps: list[RecipeStep] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
