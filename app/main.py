from fastapi import FastAPI, Request, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import pandas as pd
import csv
from io import StringIO
from .db import get_db, engine
from .models import Usuario, Base, DatoCargado
from .auth import get_password_hash, verify_password
from datetime import datetime
from io import StringIO

# Creación de tablas
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Configuración de plantillas
templates = Jinja2Templates(directory="app/templates")

# Configuración de archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Almacenamiento del usuario autenticado
current_user_id = None

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
    existing_user = db.query(Usuario).filter(
        (Usuario.nombre_usuario == username) | (Usuario.correo == email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario o el correo ya están en uso.")
    
    hashed_password = get_password_hash(password)
    new_user = Usuario(nombre_usuario=username, correo=email, contraseña=hashed_password)
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(url="/login", status_code=303)

# Inicio de sesión
@app.post("/login")
async def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    global current_user_id
    user = db.query(Usuario).filter(Usuario.nombre_usuario == username).first()
    if not user or not verify_password(password, user.contraseña):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    current_user_id = user.id_usuario
    return RedirectResponse(url="/upload", status_code=303)

# Carga de archivo CSV
@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    if file.filename.endswith('.csv'):
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))
        
        if df.empty:
            raise HTTPException(status_code=400, detail="El archivo está vacío.")
        
        # Añade el nombre del archivo a cada fila
        data = df.to_dict(orient="records")
        for row in data:
            row['nombre_archivo'] = file.filename  
        
        return templates.TemplateResponse("confirm_upload.html", {"request": request, "data": data})
    else:
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV")

# Confirmar y guardar carga

@app.post("/confirm_upload")
async def confirm_upload(request: Request, data: str = Form(...), db: Session = Depends(get_db)):
    print("Datos recibidos:", data)

    rows = [row.split(',') for row in data.split('\n')]

    for row in rows:
        if len(row) == 5:
            atributo, etiqueta, valor, categoria, resultado = row
            nuevo_registro = DatoCargado(
                id_usuario=current_user_id, 
                nombre_archivo=file.filename,
                fecha_carga=datetime.utcnow(),
                atributo=atributo,
                etiqueta=etiqueta,
                valor=valor,
                categoria=categoria,
                resultado=resultado,
            )
            db.add(nuevo_registro)

    db.commit()  
    return RedirectResponse(url="/upload", status_code=303, headers={"HX-Trigger": "datosCargados"})

@app.post("/logout")
async def logout_user():
    global current_user_id
    current_user_id = None  # Limpiar el usuario autenticado
    return RedirectResponse(url="/login", status_code=303)