from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


# 1. Die User Tabelle
class User(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relation: Ein User hat viele Workspaces
    workspaces: list["Workspace"] = Relationship(back_populates="owner")

# 2. Die Verknüpfung zur DuckDB (Das "Inhaltsverzeichnis")
class Workspace(SQLModel, table=True):
    """Verbindet einen SaaS-User mit einem Arbolab-Workspace (DuckDB)."""
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str  # Human readable name ("Stadtpark Süd")
    
    owner_id: UUID = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="workspaces")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
