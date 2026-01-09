from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel
from arbolab.core.security import LabRole

# 1. Association Table
class UserWorkspaceAssociation(SQLModel, table=True):
    __tablename__ = "user_workspace_associations"
    
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", primary_key=True)
    role: LabRole = Field(default=LabRole.VIEWER)
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="workspace_associations")
    workspace: "Workspace" = Relationship(back_populates="user_associations")

# 2. User Table
class User(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active_workspace_id: UUID | None = Field(default=None, foreign_key="workspace.id")

    # Profile fields
    full_name: str | None = Field(default=None)
    organization: str | None = Field(default=None)
    address_line1: str | None = Field(default=None)
    address_line2: str | None = Field(default=None)
    city: str | None = Field(default=None)
    zip_code: str | None = Field(default=None)
    country: str | None = Field(default=None)
    utc_offset_minutes: int | None = Field(default=None)

    workspace_associations: list["UserWorkspaceAssociation"] = Relationship(back_populates="user")
    workspaces: list["Workspace"] = Relationship(
        back_populates="users", 
        link_model=UserWorkspaceAssociation,
        sa_relationship_kwargs={"overlaps": "user,workspace_associations,user_associations,workspace"}
    )

# 3. Workspace Table
class Workspace(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    users: list["User"] = Relationship(
        back_populates="workspaces", 
        link_model=UserWorkspaceAssociation,
        sa_relationship_kwargs={"overlaps": "workspace,workspaces,user,workspace_associations"}
    )
    user_associations: list["UserWorkspaceAssociation"] = Relationship(
        back_populates="workspace",
        sa_relationship_kwargs={"overlaps": "users,workspaces"}
    )
