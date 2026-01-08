from sqlalchemy import Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from arbolab.models.base import IdMixin, TimestampMixin


class PtqBase(DeclarativeBase):
    """Base for PTQ plugin models."""
    pass

class PtqResult(PtqBase, IdMixin, TimestampMixin):
    __tablename__ = "results"
    __table_args__ = {"schema": "ptq"}
    
    label: Mapped[str] = mapped_column(String)
    score: Mapped[float] = mapped_column(Float)

def register(lab):
    """
    Registers the PTQ plugin with the Lab.
    Creates necessary tables in the 'ptq' schema.
    """
    lab.database.create_tables(PtqBase.metadata, schema="ptq")
