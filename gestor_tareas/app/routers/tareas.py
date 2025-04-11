from fastapi import APIRouter, Depends, HTTPException,status, Request, Security
from fastapi.templating import Jinja2Templates
from typing import List
from sqlalchemy.orm import Session
from .. import schemas, crud, database, models
from ..models import User
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import  HTMLResponse
from jose import JWTError, jwt  # 🔹 Importa JWTError y jwt correctamente
from app.database import get_db  # 🔹 Asegúrate de importar esta función
from app.crud import get_tasks  # Asegúrate de importar la función CRUD
import logging

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

# 👉 Extraer el token desde la cookie
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no encontrado en las cookies",
        )

    try:
        print(f"Token recibido desde cookie: {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: no contiene ID de usuario",
            )

        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
            )

        return user

    except JWTError as e:
        logging.error(f"Error al decodificar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

@router.get("/tareas", response_class=HTMLResponse)
async def mostrar_tareas(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    tareas = crud.get_tasks(db=db, user_id=current_user.id)
    return templates.TemplateResponse("tareas.html", {
        "request": request,
        "tasks": tareas,
        "user": current_user
    })

@router.post("/tareas", response_model=schemas.Task)
def create_tarea(tarea: schemas.TaskCreate, db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    return crud.create_task(db=db, tarea=tarea, user_id=current_user.id)

@router.delete("/tareas/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.delete_task(db, task_id, current_user.id)

@router.put("/tareas/{task_id}", response_model=schemas.Task)
def update_tarea(
    task_id: int, 
    tarea: schemas.TaskCreate, 
    db: Session = Depends(database.get_db), 
    current_user: User = Depends(get_current_user)
):
    return crud.update_task(db=db, task_id=task_id, tarea=tarea, user_id=current_user.id)
    