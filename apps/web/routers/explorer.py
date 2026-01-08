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

@router.get("/inspector/{entity_type}/{entity_id}", response_class=HTMLResponse)
async def explorer_inspector(entity_type: str, entity_id: int, request: Request, session: Session = Depends(get_db_session)):
    entity = await get_entity(session, entity_type, entity_id)
    return templates.TemplateResponse("partials/inspector.html", {
        "request": request,
        "entity_type": entity_type,
        "entity": entity,
        # Pass schema if needed for labels, or use entity keys
        "schema": ENTITY_MAP[entity_type]["schema"]
    })

@router.get("/form/{entity_type}", response_class=HTMLResponse)
async def explorer_form(entity_type: str, request: Request, entity_id: Optional[int] = None, redirect_url: Optional[str] = None, session: Session = Depends(get_db_session)):
    entity = None
    if entity_id:
        entity = await get_entity(session, entity_type, entity_id)
    
    schema = ENTITY_MAP[entity_type]["schema"]
    # Pydantic v2 vs v1 compat check
    fields = schema.model_fields if hasattr(schema, "model_fields") else schema.__fields__
    
    return templates.TemplateResponse("partials/modal_form.html", {
        "request": request,
        "entity_type": entity_type,
        "entity": entity,
        "fields": fields,
        "redirect_url": redirect_url
    })
