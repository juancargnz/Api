
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.database import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User

router = APIRouter()

# Define el modelo User, el hash de contraseñas, y la secret key
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función de autenticación
def authenticate_user(db: Session, username: str, password: str):
    # Busca al usuario por nombre de usuario
    user = db.query(User).filter(User.username == username).first()
    
    # Si el usuario no existe o la contraseña es incorrecta
    if not user or not verify_password(password, user.password):
        return False
    return user

# Función para verificar la contraseña
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    # Asegúrate de que el 'sub' sea una cadena (si es un número entero)
    to_encode["sub"] = str(to_encode["sub"])  # Convierte el user_id a cadena

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
# Endpoint de login
@router.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Generar el token JWT
    access_token = create_access_token(data={"sub": user.id})  # Usamos el user_id en el campo "sub"
    return {"access_token": access_token, "token_type": "bearer"}