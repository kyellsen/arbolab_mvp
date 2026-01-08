import os
from typing import Annotated

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, SQLModel, create_engine, select
from starlette.middleware.sessions import SessionMiddleware

from apps.web.core.security import get_password_hash, verify_password

# Importiere Modelle und Security
from uuid import UUID
from apps.web.models.auth import User, Workspace, UserWorkspaceAssociation
from arbolab.lab import Lab
from apps.web.core.paths import resolve_workspace_paths, ensure_workspace_paths
from pathlib import Path
from arbolab.models.core import Project
from apps.web.routers import api, explorer as explorer_router, workspaces as workspaces_router
from apps.web.core.domain import get_entity_counts

BASE_DIR = Path(__file__).resolve().parent


# 1. Datenbank Setup
from apps.web.core.database import engine, get_session, SessionDep

# DB-Erstellung erfolgt, nachdem Modelle importiert wurden
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 2. App Setup
app = FastAPI()
# WICHTIG: Session Middleware für Login-Cookies
app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_KEY_CHANGE_ME") 

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/health")
async def health():
    return {"status": "ok"}

# Register Routers
app.include_router(api.router)
app.include_router(workspaces_router.router)
app.include_router(explorer_router.router)

# ----------------- ROUTEN -----------------

@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request, 
    current_workspace: Workspace = Depends(api.get_current_workspace),
    saas_session: Session = Depends(get_session)
):
    """Dashboard oder Redirect zu Login"""
    user_data = request.session.get("user")
    if not user_data:
        return RedirectResponse(url="/auth/login")
    
    # Authenticated: Setup Lab Session manually to avoid 401 in dependencies
    try:
        user_id = UUID(str(user_data["id"]))
        
        # 1. Fetch all workspaces for context switcher
        stmt = (
            select(Workspace)
            .join(UserWorkspaceAssociation)
            .where(UserWorkspaceAssociation.user_id == user_id)
            .order_by(Workspace.created_at)
        )
        all_workspaces = saas_session.exec(stmt).all()
        
        # 2. Get Role for current workspace
        assoc = saas_session.exec(
            select(UserWorkspaceAssociation)
            .where(UserWorkspaceAssociation.user_id == user_id)
            .where(UserWorkspaceAssociation.workspace_id == current_workspace.id)
        ).first()
        
        # Should exist because Depends(get_current_workspace) found it via association
        from arbolab.core.security import LabRole
        role = assoc.role if assoc else LabRole.VIEWER

        # 3. Get Lab
        paths = resolve_workspace_paths(current_workspace.id)
        ensure_workspace_paths(paths)
        
        lab = Lab.open(
            workspace_root=paths.workspace_root,
            input_root=paths.input_root,
            results_root=paths.results_root,
            role=role
        )
        
        # 3. Use Lab Session
        with lab.database.session() as session:
            try:
                counts = await get_entity_counts(session)
            except Exception:
                counts = {} # Fallback if DB is empty/initing
            
            # Get current project name (simple logic for MVP: first project)
            project_name = "No Project Found"
            try:
                first_project = session.execute(select(Project)).scalars().first()
                if first_project:
                    project_name = first_project.name or f"Project #{first_project.id}"
            except Exception:
                pass
            
            # Template Data
            context = {
                "request": request, 
                "user": user_data,
                "counts": counts,
                "project_name": project_name,
                "current_workspace": current_workspace,
                "all_workspaces": all_workspaces,
                "role": role,
                "is_viewer": role == LabRole.VIEWER,
                "is_admin": role == LabRole.ADMIN
            }
            
            # Check HTMX request to swap only content
            if request.headers.get("HX-Request"):
                return templates.TemplateResponse("partials/dashboard_content.html", context)

            return templates.TemplateResponse("dashboard.html", context)

    except Exception as e:
        # If anything breaks in setup (e.g. malformed cookie, db error), redirect to login or show error
        # Clearing session might be safer if it's a cookie issue
        print(f"Error in home dashboard: {e}") 
        return RedirectResponse(url="/auth/login")

@app.get("/explorer", response_class=HTMLResponse)
async def explorer(request: Request):
    user = request.session.get("user")
    if not user:
         return RedirectResponse(url="/auth/login")
    
    if request.headers.get("HX-Request"):
         return templates.TemplateResponse("partials/explorer_content.html", {"request": request, "user": user})
    
    return templates.TemplateResponse("explorer.html", {"request": request, "user": user})

@app.get("/lab", response_class=HTMLResponse)
async def lab(request: Request):
    user = request.session.get("user")
    if not user:
         return RedirectResponse(url="/auth/login")
    
    if request.headers.get("HX-Request"):
         return templates.TemplateResponse("partials/lab_content.html", {"request": request, "user": user})
    
    return templates.TemplateResponse("lab.html", {"request": request, "user": user})

@app.get("/tree", response_class=HTMLResponse)
async def tree(request: Request):
    user = request.session.get("user")
    if not user:
         return RedirectResponse(url="/auth/login")
    
    if request.headers.get("HX-Request"):
         return templates.TemplateResponse("partials/tree_content.html", {"request": request, "user": user})
    
    return templates.TemplateResponse("tree.html", {"request": request, "user": user})

@app.get("/inspector/tree/{tree_id}", response_class=HTMLResponse)
async def inspector_tree(request: Request, tree_id: str):
    # Mock Details for generic tree
    return HTMLResponse(f"""
        <div class="p-4 border-b border-slate-800 flex items-center justify-between shrink-0 h-14 bg-slate-900/50 backdrop-blur">
            <h3 class="font-semibold text-slate-200">Details: Tree {tree_id}</h3>
             <button @click="rightSidebarOpen = false" class="lg:hidden text-slate-400 hover:text-white">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
        <div class="p-4 space-y-4 overflow-y-auto">
             <div class="bg-slate-800 rounded p-3">
                <p class="text-xs text-slate-500 uppercase font-bold mb-1">Status</p>
                <div class="flex items-center gap-2 text-emerald-400">
                    <span class="w-2 h-2 rounded-full bg-emerald-500"></span> Healthy
                </div>
            </div>
             <div class="bg-slate-800 rounded p-3">
                <p class="text-xs text-slate-500 uppercase font-bold mb-1">Species</p>
                <p class="text-slate-300">Quercus robur</p>
            </div>
            <div class="bg-slate-800 rounded p-3">
                <p class="text-xs text-slate-500 uppercase font-bold mb-1">Location</p>
                <p class="text-slate-300">52.5200° N, 13.4050° E</p>
            </div>
            <div class="h-40 bg-slate-800 rounded border border-slate-700 flex items-center justify-center">
                <span class="text-slate-500 text-xs">Mini-Map / Photo</span>
            </div>
        </div>
    """)

@app.get("/inspector/sensor/{sensor_id}", response_class=HTMLResponse)
async def inspector_sensor(request: Request, sensor_id: str):
     return HTMLResponse(f"""
        <div class="p-4 border-b border-slate-800 flex items-center justify-between shrink-0 h-14 bg-slate-900/50 backdrop-blur">
            <h3 class="font-semibold text-slate-200">Details: Sensor {sensor_id}</h3>
             <button @click="rightSidebarOpen = false" class="lg:hidden text-slate-400 hover:text-white">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
        <div class="p-4 space-y-4 overflow-y-auto">
             <div class="bg-slate-800 rounded p-3">
                <p class="text-xs text-slate-500 uppercase font-bold mb-1">Status</p>
                <div class="flex items-center gap-2 text-yellow-500">
                    <span class="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></span> Calibrating
                </div>
            </div>
             <div class="bg-slate-800 rounded p-3">
                <p class="text-xs text-slate-500 uppercase font-bold mb-1">Battery</p>
                <div class="w-full bg-slate-700 rounded-full h-2.5 dark:bg-gray-700">
                    <div class="bg-emerald-600 h-2.5 rounded-full" style="width: 85%"></div>
                </div>
                <p class="text-xs text-right text-slate-400 mt-1">85%</p>
            </div>
        </div>
    """)

@app.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.post("/auth/login")
async def login_submit(
    request: Request, 
    session: SessionDep,
    username: str = Form(...), # Im Formular ist es 'email', aber OAuth spec nennt es oft username
    password: str = Form(...),
):
    # User suchen
    statement = select(User).where(User.email == username)
    user = session.exec(statement).first()
    
    # Prüfen
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("auth/login.html", {
            "request": request, 
            "error": "Falsche Email oder Passwort"
        })
    
    # Session setzen (Cookie)
    request.session["user"] = {"id": str(user.id), "email": user.email}
    return RedirectResponse(url="/", status_code=303)

@app.get("/auth/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@app.post("/auth/register")
async def register_submit(
    request: Request,
    session: SessionDep,
    email: str = Form(...),
    password: str = Form(...),
    password_repeat: str = Form(...),
):
    # 1. Passwörter abgleichen
    if password != password_repeat:
        return templates.TemplateResponse("auth/register.html", {
            "request": request, 
            "error": "Die Passwörter stimmen nicht überein."
        })

    # 2. Check ob User existiert
    statement = select(User).where(User.email == email)
    if session.exec(statement).first():
         return templates.TemplateResponse("auth/register.html", {
            "request": request, 
            "error": "Email bereits registriert"
        })
    
    # 3. User anlegen
    new_user = User(email=email, hashed_password=get_password_hash(password))
    session.add(new_user)
    session.commit()
    
    return RedirectResponse(url="/auth/login", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login")
