from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel

# Role Enum
class LabRole(str, Enum):
    ADMIN = "ADMIN"
    VIEWER = "VIEWER"

# Association Table
class UserWorkspaceAssociation(SQLModel, table=True):
    __tablename__ = "user_workspace_associations"
    
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", primary_key=True)
    role: LabRole = Field(default=LabRole.VIEWER)
    
    # Optional: Timestamps for audit
    joined_at: datetime = Field(default_factory=datetime.utcnow)

# 1. Die User Tabelle
class User(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relation: Many-to-Many via Association
    workspace_associations: list["UserWorkspaceAssociation"] = Relationship(back_populates="user") # Keep for direct access to association fields
    workspaces: list["Workspace"] = Relationship(back_populates="users", link_model=UserWorkspaceAssociation)

# 2. Die Verknüpfung zur DuckDB (Das "Inhaltsverzeichnis")
class Workspace(SQLModel, table=True):
    """Verbindet einen SaaS-User mit einem Arbolab-Workspace (DuckDB)."""
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str  # Human readable name ("Stadtpark Süd")
    
    # No more single owner_id, relationship is now through Association
    users: list["User"] = Relationship(back_populates="workspaces", link_model=UserWorkspaceAssociation)
    user_associations: list["UserWorkspaceAssociation"] = Relationship(back_populates="workspace")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
