from sqlalchemy import Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from arbolab.models.base import IdMixin, TimestampMixin


class Ls3Base(DeclarativeBase):
    """Base for LineScale3 plugin models."""
    pass

class Ls3Result(Ls3Base, IdMixin, TimestampMixin):
    __tablename__ = "results"
    __table_args__ = {"schema": "ls3"}
    
    label: Mapped[str] = mapped_column(String)
    score: Mapped[float] = mapped_column(Float)

def register(lab):
    """
    Registers the LineScale3 plugin with the Lab.
    Creates necessary tables in the 'ls3' schema.
    """
    lab.database.create_tables(Ls3Base.metadata, schema="ls3")
