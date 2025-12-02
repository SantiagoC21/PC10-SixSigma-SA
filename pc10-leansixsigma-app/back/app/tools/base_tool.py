# backend/app/tools/base_tool.py
from abc import ABC, abstractmethod
import pandas as pd
from app.schemas import AnalysisResult

class SixSigmaTool(ABC):
    """
    Clase abstracta que todas las herramientas deben heredar.
    """
    
    def __init__(self, data: list, params: dict):
        # Convertimos automáticamente la entrada JSON a Pandas DataFrame
        self.df = pd.DataFrame(data)
        self.params = params

    @abstractmethod
    def analyze(self) -> AnalysisResult:
        """
        Método obligatorio donde ocurre la magia matemática.
        Debe retornar un objeto AnalysisResult.
        """
        pass

    def validate_columns(self, required_columns: list):
        """Helper para verificar que el Excel subido tenga las columnas correctas"""
        missing = [col for col in required_columns if col not in self.df.columns]
        if missing:
            raise ValueError(f"Faltan las columnas requeridas: {', '.join(missing)}")