from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AnalysisRequest, AnalysisResult
from app.services.tool_factory import ToolFactory
from fastapi import HTTPException

# Inicializar la aplicación
app = FastAPI(
    title="Six Sigma Desktop Backend",
    description="Motor de cálculo e IA para herramientas DMAIC",
    version="1.0.0"
)

# Configuración de CORS (Permite que Electron hable con Python)
origins = [
    "http://localhost",
    "http://localhost:3000",  # Puerto común de React/Electron en desarrollo
    "*"                       # En producción, esto se puede restringir más
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend Six Sigma Operativo", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "running"}

@app.post("/api/v1/analyze", response_model=AnalysisResult)
def run_analysis(request: AnalysisRequest):
    try:
        # 1. Llamar a la fábrica para obtener la clase correcta
        ToolClass = ToolFactory.get_tool(request.tool_name)
        
        # 2. Instanciar la herramienta con los datos
        tool_instance = ToolClass(data=request.data, params=request.parameters)
        
        # 3. Ejecutar análisis
        result = tool_instance.analyze()
        
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")