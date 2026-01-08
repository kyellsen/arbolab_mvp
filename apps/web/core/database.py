from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine
from arbolab.config import load_config

# 1. Datenbank Setup
config = load_config()
config.ensure_directories()

# Use configured DB URL or fallback to local sqlite (though Postgres is desired)
database_url = config.database_url
if not database_url:
    # Fallback to sqlite in data_root for local dev without containers
    sqlite_file_name = config.data_root / "saas.db"
    database_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(database_url)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
