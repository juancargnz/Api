# Funciones CRUD
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import Task
from . import models, schemas


def get_tasks(db: Session, user_id: int):
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
    
