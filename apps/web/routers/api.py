from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Any
from apps.web.core.domain import list_entities, get_entity, create_entity, update_entity, delete_entity
from arbolab.lab import Lab
from pathlib import Path

router = APIRouter(prefix="/api/entities", tags=["entities"])

# Helper to get the Lab instance. 
# In a real SaaS, this would resolve the lab based on the current user's selected project.
# For now, we use a default workspace.
def get_lab() -> Lab:
    # Use the data_root from config to find the workspace
    from arbolab.config import load_config
    config = load_config()
    workspace_root = config.data_root / "workspace"
    return Lab.open(workspace_root)

def get_db_session(lab: Lab = Depends(get_lab)):
    with lab.database.session() as session:
        yield session

@router.get("/{entity_type}")
async def api_list_entities(entity_type: str, search: str = None, tag: str = None, session: Session = Depends(get_db_session)):
    try:
        return await list_entities(session, entity_type, search=search, tag=tag)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{entity_type}/{entity_id}")
async def api_get_entity(entity_type: str, entity_id: int, session: Session = Depends(get_db_session)):
    entity = await get_entity(session, entity_type, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.post("/{entity_type}")
async def api_create_entity(entity_type: str, data: dict[str, Any], session: Session = Depends(get_db_session)):
    try:
        return await create_entity(session, entity_type, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{entity_type}/{entity_id}")
async def api_update_entity(entity_type: str, entity_id: int, data: dict[str, Any], session: Session = Depends(get_db_session)):
    try:
        entity = await update_entity(session, entity_type, entity_id, data)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{entity_type}/{entity_id}")
async def api_delete_entity(entity_type: str, entity_id: int, session: Session = Depends(get_db_session)):
    try:
        success = await delete_entity(session, entity_type, entity_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entity not found")
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
