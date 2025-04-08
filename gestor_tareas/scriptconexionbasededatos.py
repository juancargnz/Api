from app.database import SessionLocal
from app import models

# Establece la sesión de la base de datos
db = SessionLocal()

try:
    # Ejecuta una consulta simple para ver si se está conectando
    result = db.execute("SELECT 1")  # Consulta simple para probar la conexión
    print("Conexión exitosa a la base de datos.")
    
    # También puedes verificar si existen usuarios en la base de datos
    users = db.query(models.User).all()
    print(f"Usuarios en la base de datos: {users}")
    
except Exception as e:
    print(f"Error al conectar con la base de datos: {e}")

finally:
    # Asegúrate de cerrar la sesión
    db.close()

