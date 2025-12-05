from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_db_and_tables
from app.api import analysis_routes # Importamos las rutas que acabamos de crear

app = FastAPI(
    title="Six Sigma Desktop Engine",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicio: Crear tablas en la DB
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# CONECTAR LAS RUTAS (El paso clave)
# Ahora las URLs serán: /api/v1/analyze, /api/v1/recommend
app.include_router(analysis_routes.router, prefix="/api/v1", tags=["Herramientas Six Sigma"])

@app.get("/")
def read_root():
    return {"system": "Online", "database": "SQLite Connected"}