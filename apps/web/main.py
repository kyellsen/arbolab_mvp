import os
from typing import Annotated

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, SQLModel, create_engine, select
from starlette.middleware.sessions import SessionMiddleware

from apps.web.core.security import get_password_hash, verify_password

# Importiere Modelle und Security
from apps.web.models.auth import User
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


# 1. Datenbank Setup
from arbolab.config import load_config

config = load_config()
config.ensure_directories()

# Use configured DB URL or fallback to local sqlite (though Postgres is desired)
database_url = config.database_url
if not database_url:
    # Fallback to sqlite in data_root for local dev without containers
    sqlite_file_name = config.data_root / "saas.db"
    database_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(database_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

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

# ----------------- ROUTEN -----------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Dashboard oder Redirect zu Login"""
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/auth/login")
    
    # Check HTMX request to swap only content
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse("partials/dashboard_content.html", {"request": request, "user": user})

    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

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
    request.session["user"] = {"id": user.id, "email": user.email}
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
