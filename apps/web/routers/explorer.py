from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import os
from pathlib import Path

from apps.web.core.domain import list_entities, get_entity, ENTITY_MAP
from apps.web.routers.api import get_db_session

router = APIRouter(prefix="/explorer-ui", tags=["explorer-ui"])
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/list/{entity_type}", response_class=HTMLResponse)
async def explorer_list(entity_type: str, request: Request, search: str = None, tag: str = None, session: Session = Depends(get_db_session)):
    entities = await list_entities(session, entity_type, search=search, tag=tag)
    return templates.TemplateResponse("partials/entity_list.html", {
        "request": request,
        "entity_type": entity_type,
        "entities": entities
    })

@router.get("/form/{entity_type}", response_class=HTMLResponse)
async def explorer_form(entity_type: str, request: Request, entity_id: Optional[int] = None, session: Session = Depends(get_db_session)):
    entity = None
    if entity_id:
        entity = await get_entity(session, entity_type, entity_id)
    
    # We can inspect the schema to build the form dynamically or just use the entity object
    schema = ENTITY_MAP[entity_type]["schema"]
    fields = schema.__fields__ if hasattr(schema, "__fields__") else schema.model_fields
    
    return templates.TemplateResponse("partials/entity_form.html", {
        "request": request,
        "entity_type": entity_type,
        "entity": entity,
        "fields": fields
    })
