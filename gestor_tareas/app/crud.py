# Funciones CRUD
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, TaskCreate
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import Task
from . import models, schemas
from fastapi import HTTPException


def get_tasks(db: Session, user_id: int):
    print(db.query(Task).filter(Task.user_id == user_id))
    return db.query(Task).filter(Task.user_id == user_id).all()

# Crea un contexto para la encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para encriptar contraseñas
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Función para crear un nuevo usuario
def create_user(db: Session, user: UserCreate):
    hashed_password = hash_password(user.password)  # Encripta la contraseña
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_task(db: Session, tarea: schemas.TaskCreate, user_id: int):
    db_task = models.Task(
        title=tarea.title,
        description=tarea.description,
        state=tarea.state,
        user_id=user_id  # Asociamos la tarea al usuario
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
    
# Eliminar una tarea
def delete_task(db: Session, task_id: int, user_id: int):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    db.delete(task)
    db.commit()
    return {"message": "Tarea eliminada correctamente"}

def update_task(db: Session, task_id: int, tarea: schemas.TaskCreate, user_id: int):
    # Buscar la tarea en la base de datos
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # Actualizar los campos de la tarea
    task.title = tarea.title
    task.description = tarea.description
    task.state = tarea.state

    # Guardar los cambios en la base de datos
    db.commit()
    db.refresh(task)
    return task