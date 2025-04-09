# Esquemas de validación de datos con Pydantic
from pydantic import BaseModel
from typing import List, Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    state: str

class TaskCreate(BaseModel):
    title: str
    description: str
    state: str  # Asegúrate de que el campo state esté incluido

    class Config:
        orm_mode = True
        
class Task(TaskBase):
    id: int
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    tasks: List[Task] = []
    class Config:
        orm_mode = True
class TaskDelete(BaseModel):
    task_id: int
