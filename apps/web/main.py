import os
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, SQLModel, create_engine, select
from starlette.middleware.sessions import SessionMiddleware

from apps.web.core.security import get_password_hash, verify_password
from apps.web.core.access_log import access_log_middleware

# Importiere Modelle und Security
from uuid import UUID
from apps.web.models.auth import Workspace, UserWorkspaceAssociation
from apps.web.models.user import User
from apps.web.core.lab_cache import get_cached_lab
from pathlib import Path
from arbolab.models.core import Project
from apps.web.routers import api, explorer as explorer_router, workspaces as workspaces_router, settings as settings_router, logs as logs_router
from apps.web.core.domain import get_entity_counts, ENTITY_MAP
from arbolab.core.recipes.executor import RecipeExecutor

BASE_DIR = Path(__file__).resolve().parent


# 1. Datenbank Setup
from apps.web.core.database import engine, get_session, SessionDep

# DB-Erstellung erfolgt, nachdem Modelle importiert wurden
def create_db_and_tables() -> None:
    """Create the SaaS tables if they do not exist yet."""
    SQLModel.metadata.create_all(engine)


def run_migrations() -> None:
    """Apply Alembic migrations for the SaaS database."""
    from alembic import command
    from alembic.config import Config

    alembic_ini = BASE_DIR / "alembic.ini"
    alembic_config = Config(str(alembic_ini))
    alembic_config.set_main_option("script_location", str(BASE_DIR / "migrations"))
    command.upgrade(alembic_config, "head")

# 2. App Setup
app = FastAPI()
# WICHTIG: Session Middleware für Login-Cookies
app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_KEY_CHANGE_ME") 
app.middleware("http")(access_log_middleware)

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def resolve_workspace_context(request: Request, session: Session) -> tuple[Workspace | None, list[Workspace]]:
    user_data = request.session.get("user")
    if not user_data:
        return None, []

    try:
        user_id = UUID(str(user_data["id"]))
    except (ValueError, TypeError, KeyError):
        return None, []

    user = session.get(User, user_id)
    if not user:
        return None, []

    current_workspace = None
    active_ws_id = request.session.get("active_workspace_id")
    if active_ws_id:
        try:
            stmt = (
                select(Workspace)
                .join(UserWorkspaceAssociation)
                .where(Workspace.id == UUID(active_ws_id))
                .where(UserWorkspaceAssociation.user_id == user_id)
            )
            current_workspace = session.exec(stmt).first()
        except (ValueError, TypeError):
            current_workspace = None

    stmt = (
        select(Workspace)
        .join(UserWorkspaceAssociation)
        .where(UserWorkspaceAssociation.user_id == user_id)
        .order_by(Workspace.created_at)
    )
    all_workspaces = session.exec(stmt).all()

    if not current_workspace and user and user.last_active_workspace_id:
        for workspace in all_workspaces:
            if workspace.id == user.last_active_workspace_id:
                current_workspace = workspace
                break

    if not current_workspace and all_workspaces:
        current_workspace = all_workspaces[0]

    if current_workspace:
        request.session["active_workspace_id"] = str(current_workspace.id)
        if user.last_active_workspace_id != current_workspace.id:
            user.last_active_workspace_id = current_workspace.id
            session.add(user)
            session.commit()

    return current_workspace, all_workspaces

@app.on_event("startup")
def on_startup() -> None:
    """Initialize the database and seed default data on startup."""
    import time
    from sqlalchemy.exc import OperationalError
    
    # 1. Create Tables
    max_retries = 10
    retry_delay = 2
    for i in range(max_retries):
        try:
            create_db_and_tables()
            run_migrations()
            print("Database connected, tables verified, and migrations applied.")
            break
        except OperationalError as e:
            if i < max_retries - 1:
                print(f"Postgres not ready (attempt {i+1}/{max_retries}), waiting...")
                time.sleep(retry_delay)
            else:
                print("Could not connect to database after multiple retries.")
                raise e

    # 2. Run Seeder
    from apps.web.core import seeder
    try:
        seeder.run_seed()
    except Exception as e:
        print(f"Error during seeding: {e}")

@app.get("/health")
async def health():
    return {"status": "ok"}

# Register Routers
app.include_router(api.router)
app.include_router(workspaces_router.router)
app.include_router(explorer_router.router)
app.include_router(settings_router.router)
app.include_router(logs_router.router)

# ----------------- ROUTEN -----------------

@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request, 
    saas_session: Session = Depends(get_session)
):
    """Dashboard oder Redirect zu Login"""
    user_data = request.session.get("user")
    if not user_data:
        return RedirectResponse(url="/auth/login")
    
    # Authenticated: Setup Lab Session manually to avoid 401 in dependencies
    try:
        user_id = UUID(str(user_data["id"]))

        user = saas_session.get(User, user_id)
        if not user:
            return RedirectResponse(url="/auth/login")
        
        # 1. Try Session for Workspace ID
        active_ws_id = request.session.get("active_workspace_id")
        current_workspace = None
        
        if active_ws_id:
            try:
                stmt = (
                    select(Workspace)
                    .join(UserWorkspaceAssociation)
                    .where(Workspace.id == UUID(active_ws_id))
                    .where(UserWorkspaceAssociation.user_id == user_id)
                )
                current_workspace = saas_session.exec(stmt).first()
            except Exception:
                pass

        if not current_workspace and user.last_active_workspace_id:
            stmt = (
                select(Workspace)
                .join(UserWorkspaceAssociation)
                .where(Workspace.id == user.last_active_workspace_id)
                .where(UserWorkspaceAssociation.user_id == user_id)
            )
            current_workspace = saas_session.exec(stmt).first()
        
        if not current_workspace:
             # Fallback: First available
            stmt = (
                select(Workspace)
                .join(UserWorkspaceAssociation)
                .where(UserWorkspaceAssociation.user_id == user_id)
                .order_by(Workspace.created_at)
            )
            current_workspace = saas_session.exec(stmt).first()
            
        if not current_workspace:
             # Show Onboarding Overlay instead of redirect
             context = {
                "request": request, 
                "user": user_data,
                "counts": {},
                "project_name": "Neues Lab",
                "current_workspace": None,
                "all_workspaces": [],
                "role": None,
                "is_viewer": False,
                "is_admin": False,
                "show_onboarding": True
            }
             return templates.TemplateResponse("dashboard.html", context)

        request.session["active_workspace_id"] = str(current_workspace.id)
        if user.last_active_workspace_id != current_workspace.id:
            user.last_active_workspace_id = current_workspace.id
            saas_session.add(user)
            saas_session.commit()
        
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
        lab = get_cached_lab(current_workspace.id, role)
        
        # 3. Use Lab Session
        with lab.database.session() as session:
            try:
                counts = await get_entity_counts(session)
            except Exception:
                counts = {} # Fallback if DB is empty/initing
            
            # Fetch Recipe History
            recipe = RecipeExecutor.load_recipe(lab)
            recent_activity = recipe.steps[::-1] # Show latest first
            
            # Get current project name (simple logic for MVP: first project)
            try:
                first_project = session.execute(select(Project)).scalars().first()
                if first_project:
                    project_name = first_project.name or f"Project #{first_project.id}"
                else: 
                     # Fallback to Workspace name if empty lab
                     project_name = current_workspace.name
            except Exception:
                 project_name = current_workspace.name
            
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
                "is_admin": role == LabRole.ADMIN,
                "show_onboarding": False,
                "recent_activity": recent_activity
            }
            
            # Check HTMX request to swap only content (but not boosted full-page nav)
            if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
                return templates.TemplateResponse("partials/dashboard_content.html", context)

            return templates.TemplateResponse("dashboard.html", context)

    except Exception as e:
        # If anything breaks in setup (e.g. malformed cookie, db error), redirect to login or show error
        # Clearing session might be safer if it's a cookie issue
        print(f"Error in home dashboard: {e}") 
        return RedirectResponse(url="/auth/login")

@app.get("/explorer", response_class=HTMLResponse)
async def explorer(
    request: Request,
    entity: Optional[str] = None,
    open_form: Optional[str] = None,
    saas_session: Session = Depends(get_session),
):
    user = request.session.get("user")
    if not user:
         return RedirectResponse(url="/auth/login")

    current_workspace, all_workspaces = resolve_workspace_context(request, saas_session)

    active_entity = "project"
    entity_param = None
    if entity:
        normalized_entity = entity.strip().lower()
        if normalized_entity in ENTITY_MAP:
            active_entity = normalized_entity
            entity_param = normalized_entity

    open_form_entity = None
    if open_form:
        normalized_form = open_form.strip().lower()
        if normalized_form in ENTITY_MAP:
            open_form_entity = normalized_form
            if entity_param is None:
                active_entity = normalized_form

    context = {
        "request": request,
        "user": user,
        "active_entity": active_entity,
        "open_form_entity": open_form_entity,
        "current_workspace": current_workspace,
        "all_workspaces": all_workspaces,
    }

    if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
         return templates.TemplateResponse("partials/explorer_content.html", context)

    return templates.TemplateResponse("explorer.html", context)

@app.get("/analysis", response_class=HTMLResponse)
async def analysis(
    request: Request,
    saas_session: Session = Depends(get_session),
):
    user = request.session.get("user")
    if not user:
         return RedirectResponse(url="/auth/login")

    current_workspace, all_workspaces = resolve_workspace_context(request, saas_session)
    context = {
        "request": request,
        "user": user,
        "current_workspace": current_workspace,
        "all_workspaces": all_workspaces,
    }
    
    if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
         return templates.TemplateResponse("partials/analysis_content.html", context)
    
    return templates.TemplateResponse("analysis.html", context)

@app.get("/tree", response_class=HTMLResponse)
async def tree(
    request: Request,
    current_workspace: Workspace = Depends(api.get_current_workspace),
    saas_session: Session = Depends(get_session)
):
    user_data = request.session.get("user")
    if not user_data:
         return RedirectResponse(url="/auth/login")
    
    all_workspaces = []
    # Authenticated: Setup Lab Session manually
    try:
        user_id = UUID(str(user_data["id"]))
        stmt = (
            select(Workspace)
            .join(UserWorkspaceAssociation)
            .where(UserWorkspaceAssociation.user_id == user_id)
            .order_by(Workspace.created_at)
        )
        all_workspaces = saas_session.exec(stmt).all()
        
        # 1. Get Role for current workspace
        assoc = saas_session.exec(
            select(UserWorkspaceAssociation)
            .where(UserWorkspaceAssociation.user_id == user_id)
            .where(UserWorkspaceAssociation.workspace_id == current_workspace.id)
        ).first()
        
        from arbolab.core.security import LabRole
        role = assoc.role if assoc else LabRole.VIEWER

        # 2. Get Lab
        lab = get_cached_lab(current_workspace.id, role)
        
        # 3. Use Lab Session to get counts
        with lab.database.session() as session:
            try:
                counts = await get_entity_counts(session)
            except Exception:
                counts = {} 
            
            context = {
                "request": request, 
                "user": user_data,
                "counts": counts,
                "current_workspace": current_workspace,
                "all_workspaces": all_workspaces,
            }

            if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
                 return templates.TemplateResponse("partials/tree_content.html", context)
            
            return templates.TemplateResponse("tree.html", context)

    except Exception as e:
        print(f"Error in tree view: {e}")
        # Build context with empty counts on error to avoid crash
        context = {
            "request": request, 
            "user": user_data,
            "counts": {},
            "current_workspace": current_workspace,
            "all_workspaces": all_workspaces,
        }
        if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
             return templates.TemplateResponse("partials/tree_content.html", context)
        return templates.TemplateResponse("tree.html", context)

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
