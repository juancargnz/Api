"""# Endpoints de gestión de tareas
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from .. import schemas, crud, database, models
from ..models import User
from fastapi.security import OAuth2PasswordBearer
from fastapi import Security, status
from jose import JWTError, jwt  # 🔹 Importa JWTError y jwt correctamente
from app.database import get_db  # 🔹 Asegúrate de importar esta función
from app.crud import get_tasks  # Asegúrate de importar la función CRUD

router = APIRouter()

# Indica que el token debe venir en el encabezado Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

# Dependencia para obtener el usuario actual
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        print(f"Token recibido: {token}")
        # Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        print(f"Payload decodificado: {payload}")

        user_id: int = payload.get("sub")  # El 'sub' contiene el user_id

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        # Buscar al usuario por su ID en la base de datos
        user = db.query(models.User).filter(models.User.id == user_id).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return user  # Retorna el objeto User

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

@router.get("/tareas", response_model=List[schemas.Task])
def get_tareas(db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    return crud.get_tasks(db=db, user_id=current_user.id)

@router.post("/tareas", response_model=schemas.Task)
def create_tarea(tarea: schemas.TaskCreate, db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    return crud.create_task(db=db, tarea=tarea, user_id=current_user.id)
"""
from fastapi import APIRouter, Depends, HTTPException,status
from typing import List
from sqlalchemy.orm import Session
from .. import schemas, crud, database, models
from ..models import User
from fastapi.security import OAuth2PasswordBearer
from fastapi import Security, status
from jose import JWTError, jwt  # 🔹 Importa JWTError y jwt correctamente
from app.database import get_db  # 🔹 Asegúrate de importar esta función
from app.crud import get_tasks  # Asegúrate de importar la función CRUD
import logging

router = APIRouter()

# Indicamos que el token debe venir en el encabezado Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

# Dependencia para obtener el usuario actual
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        print(f"Token recibido: {token}")
        # Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        print(f"Payload decodificado: {payload}")

        user_id: int = payload.get("sub")  # El 'sub' contiene el user_id

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        # Buscar al usuario por su ID en la base de datos
        user = db.query(models.User).filter(models.User.id == user_id).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return user  # Retorna el objeto User

    except JWTError as e:
        logging.error(f"Error decodificando el token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

@router.get("/tareas", response_model=List[schemas.Task])
def get_tareas(db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    return crud.get_tasks(db=db, user_id=current_user.id)

@router.post("/tareas", response_model=schemas.Task)
def create_tarea(tarea: schemas.TaskCreate, db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    return crud.create_task(db=db, tarea=tarea, user_id=current_user.id)
