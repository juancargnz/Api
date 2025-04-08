from app.database import SessionLocal
from app.schemas import UserCreate
from app import crud  # Asegúrate de importar crud correctamente

# Inicia la sesión de base de datos
db = SessionLocal()

# Define un usuario que deseas agregar
new_user = UserCreate(username="usuario1", password="disofic")

# Llama a la función para agregar el usuario a la base de datos
created_user = crud.create_user(db=db, user=new_user)

# Imprime el usuario creado para confirmar
print(f"Usuario creado: {created_user.username}")

# Cierra la sesión de base de datos
db.close()

