from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Define la URL de la base de datos (ajústalo según tu configuración)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # o tu configuración de base de datos real

# Crear el motor de la base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Crear SessionLocal (la sesión para interactuar con la base de datos)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea todas las tablas en la base de datos (esto debería ejecutarse cuando inicies la aplicación)
Base.metadata.create_all(bind=engine)

def get_db():
    # Crea la sesión de la base de datos
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

