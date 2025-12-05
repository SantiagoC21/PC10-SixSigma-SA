from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from app.schemas import AnalysisRequest, AnalysisResult, RecommendationRequest
from app.services.tool_factory import ToolFactory
from app.services.recommender import ToolRecommender
from app.core.database import get_session
from app.domain.models import Analysis

# Creamos un "Router" que luego conectaremos al main
router = APIRouter()

# Instancia del recomendador
recommender = ToolRecommender()

@router.post("/analyze", response_model=AnalysisResult)
def run_analysis(request: AnalysisRequest, db: Session = Depends(get_session)):
    """
    Endpoint principal que ejecuta cualquier herramienta estadística.
    """
    try:
        # 1. Fábrica
        ToolClass = ToolFactory.get_tool(request.tool_name)
        # 2. Instancia y Ejecución
        tool_instance = ToolClass(data=request.data, params=request.parameters)
        result = tool_instance.analyze()
        
        # (Opcional) Aquí podrías guardar automáticamente el log en la DB
        # save_analysis_log(db, request, result)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/recommend")
def get_recommendations(request: RecommendationRequest):
    """
    Endpoint de IA para recomendar herramientas.
    """
    try:
        results = recommender.recommend(request.phase, request.description)
        return {"status": "success", "recommendations": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))