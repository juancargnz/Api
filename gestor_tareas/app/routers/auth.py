from fastapi import APIRouter, Depends, HTTPException, status, Body, Form, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.database import get_db
from fastapi.security import OAuth2PasswordBearer
from app.models import User
from app import schemas
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List
from app.schemas import UserCreate
from app import database, models, crud

# Configuración de seguridad y JWT
SECRET_KEY = "mysecretkey"  # 🔒 Cambia esto en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Verifica contraseña
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Hashea contraseña
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Crear usuario
def create_user(db: Session, user: UserCreate):
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Autentica usuario
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return False
    return user

# Crear token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Página de login
@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Procesar login
@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

    # ✅ Usa el ID del usuario en el token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Redirección con cookie
    response = RedirectResponse(url="http://localhost:3333/index", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 60 * 24,
        secure=False,  # Cámbialo a True si usas HTTPS
        samesite="lax"
    )

    return response

# Obtener usuario actual desde la cookie
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no encontrado")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

        try:
            user_id = int(user_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ID de usuario inválido")

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        return user
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

# Página principal protegida
@router.get("/index", response_class=HTMLResponse)
async def index(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    title = "Gestor de Tareas"
    content = f"Bienvenido, {current_user.username}, al Gestor de Tareas"
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": title,
        "content": content,
        "tareas_url": "/tareas"
    })
