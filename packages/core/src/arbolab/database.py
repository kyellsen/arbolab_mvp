from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import duckdb
from arbolab_logger import get_logger
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

# Import core models to ensure they are registered in Base.metadata
import arbolab.models.core  # noqa: F401
from arbolab.models.base import Base

logger = get_logger(__name__)

class WorkspaceDatabase:
    """
    Manages the DuckDB connection for domain entities and metadata.
    """
    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._engine = None
        self._session_factory = None
        
    def connect(self):
        """Initializes the engine and session factory."""
        if self._engine is not None:
            return

        # DuckDB via SQLAlchemy
        # Ensure the directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn_str = f"duckdb:///{self._db_path}"
        logger.debug(f"Connecting to database at {self._db_path}")
        self._engine = create_engine(conn_str)
        
        # Initialize Schema (MVP: Create all tables if missing)
        # Core tables go to default schema (or 'main' if configured, but default is easier for now)
        self.create_tables(Base.metadata)
        
        self._session_factory = sessionmaker(bind=self._engine)
        
        # Register event listeners for logging
        event.listen(self._session_factory, "after_flush", self._log_after_flush)

    def ensure_schema(self, schema_name: str):
        """Ensures a DuckDB schema (namespace) exists."""
        if self._engine is None:
            self.connect()
            
        with self._engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            
    def create_tables(self, metadata, schema: str | None = None):
        """
        Creates tables from the given metadata.
        If schema is provided, ensures the schema exists first.
        """
        if self._engine is None:
            self.connect()

        if schema:
            self.ensure_schema(schema)
            
        # SQLAlchemy create_all handles checking existence
        metadata.create_all(self._engine)

    def _log_after_flush(self, session, flush_context):
        """Log created, updated, or deleted entities."""
        for obj in session.new:
            logger.info(f"Created {type(obj).__name__}: {obj}")
        for obj in session.dirty:
            logger.debug(f"Updated {type(obj).__name__}: {obj}")
        for obj in session.deleted:
            logger.info(f"Deleted {type(obj).__name__}: {obj}")

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Yields a SQLAlchemy session.
        Context Manager usage: with lab.database.session() as db: ...
        """
        if self._session_factory is None:
            self.connect()
            
        session = self._session_factory()
        # Session ID for tracing (simple hash of object)
        sid = id(session)
        logger.debug(f"[Session {sid}] Started transaction")
        try:
            yield session
            logger.debug(f"[Session {sid}] Committing transaction...")
            session.commit()
            logger.debug(f"[Session {sid}] Committed transaction successfully")
        except Exception as e:
            logger.error(f"[Session {sid}] Transaction failed: {e}")
            session.rollback()
            logger.debug(f"[Session {sid}] Rolled back transaction")
            raise
        finally:
            session.close()
            logger.debug(f"[Session {sid}] Session closed")

    def get_native_con(self):
        """
        Returns a native duckdb connection for analytical heavy lifting 
        if SA is too slow or limiting.
        """
        if self._engine is None:
            self.connect()
        # This is a bit of a hack in some SA versions, but usually getting a raw connection is possible
        # For simplicity in MVP, we might just open a read-only cursor or use the engine connection.
        return duckdb.connect(str(self._db_path))
