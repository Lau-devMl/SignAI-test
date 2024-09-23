from fastapi import FastAPI, Request, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .db import get_db, engine
from .models import Usuario, Base
from .auth import get_password_hash, verify_password

# Creación de tablas
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuración de plantillas
templates = Jinja2Templates(directory="app/templates")

# Configuración de archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Rutas
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# Registro de usuario
@app.post("/register")
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verificación de nombre de usuario y contraseña
    existing_user = db.query(Usuario).filter((Usuario.nombre_usuario == username) | (Usuario.correo == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario o el correo ya están en uso.")
    
    # Hashear la contraseña
    hashed_password = get_password_hash(password)
    
    # Crear nuevo usuario
    new_user = Usuario(nombre_usuario=username, correo=email, contraseña=hashed_password)
    db.add(new_user)
    db.commit()
    
    #redirigir a la página de inicio de sesión
    return RedirectResponse(url="/login", status_code=303)

# Inicio de sesión
@app.post("/login")
async def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(Usuario).filter(Usuario.nombre_usuario == username).first()
        if not user or not verify_password(password, user.contraseña):
            raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
        
        return templates.TemplateResponse("upload.html", {"request": request})
    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "msg": f"Error al iniciar sesión: {e}"})

# Carga de archivo
@app.post("/upload")
async def handle_upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    return {"message": f"Archivo {file.filename} cargado exitosamente"}
