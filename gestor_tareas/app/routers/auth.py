from fastapi import APIRouter, Depends, HTTPException, status, Body, Form, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.database import get_db
from fastapi.security import OAuth2PasswordBearer
from app.models import User
from app import schemas  # O importa Task específicamente si prefieres hacerlo así.
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List
from app.schemas import UserCreate
from app import database
from app import models
from fastapi.responses import RedirectResponse



# Configuración de seguridad y JWT
SECRET_KEY = "mysecretkey"  # Cambia esto a una clave más segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer se usa para definir cómo se debe recibir el token en las solicitudes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Crear instancia de Jinja2Templates para renderizar HTML
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# Función de autenticación
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return False
    return user

# Función para verificar la contraseña
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Función para encriptar la contraseña
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Función para crear un nuevo usuario
def create_user(db: Session, user: UserCreate):
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Función para crear el token de acceso (JWT)
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    to_encode["sub"] = str(to_encode["sub"])  # Aseguramos que sub sea una cadena (ID del usuario)

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Endpoint para procesar el login
@router.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    # Buscar el usuario en la base de datos
    user = db.query(models.User).filter(models.User.username == username).first()
    
    # Verificar si el usuario existe y si la contraseña es correcta
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

    # Crear el token de acceso
    access_token = create_access_token(data={"sub": user.username})

    # Devolver el token como JSON
    return {"token": access_token}

# Función para obtener el usuario actual basado en el token (verificación)
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no válido")
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no válido")
        
@router.get("/tareas", response_class=HTMLResponse)
async def tareas(request: Request, db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado")
    
    # Aquí puedes obtener las tareas del usuario
    tasks = crud.get_tasks(db, user_id=current_user.id)
    
    return templates.TemplateResponse("tareas.html", {"request": request, "tasks": tasks})



@router.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    title = "Gestor de Tareas"
    content = "Bienvenido al Gestor de Tareas"
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": title,
        "content": content,
        "tareas_url": "/tareas"  # Pasamos la URL a la plantilla
    })

