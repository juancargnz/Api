from fastapi import FastAPI
from .routers import auth, tareas
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import os
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.staticfiles import StaticFiles
app = FastAPI()
# Montar el directorio de archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar Jinja2 para que lea las plantillas desde app/templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# 🔹 Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3333"],  # Permitir solicitudes desde el frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)


app.include_router(auth.router)
app.include_router(tareas.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
