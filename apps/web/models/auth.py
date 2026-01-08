from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


# 1. Die User Tabelle
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relation: Ein User hat viele Projekte
    projects: list["ProjectLink"] = Relationship(back_populates="owner")

# 2. Die Verknüpfung zur DuckDB (Das "Inhaltsverzeichnis")
class ProjectLink(SQLModel, table=True):
    """Verbindet einen SaaS-User mit einem Arbolab-Workspace (DuckDB)."""
    id: int | None = Field(default=None, primary_key=True)
    project_uuid: str = Field(index=True) # Die ID des Ordners im Dateisystem
    name: str  # Human readable name ("Stadtpark Süd")
    
    owner_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="projects")
