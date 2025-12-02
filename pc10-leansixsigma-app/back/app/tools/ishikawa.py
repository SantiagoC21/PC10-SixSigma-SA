# backend/app/tools/ishikawa.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class IshikawaTool(SixSigmaTool):
    """
    Herramienta Diagrama de Causa-Efecto (Ishikawa / Espina de Pescado).
    Clasifica y estructura causas en las 6M.
    Referencias:
    - Libro Seis Sigma y sus Aplicaciones, pág 37 (Diagrama de Causa y Efecto).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren causas para generar el diagrama.")

        required_cols = ["category", "cause"]
        self.validate_columns(required_cols)

        # Normalizar categorías (Capitalizar para evitar duplicados por mayúsculas/minúsculas)
        self.df["category"] = self.df["category"].str.title().str.strip()

        # 2. Estructuración (Agrupar por Categoría/M)
        # El objetivo es crear un objeto JSON donde cada clave es una "Espina" mayor
        fishbone_structure = {}
        
        # Obtenemos las categorías únicas presentes en los datos
        categories_found = self.df["category"].unique()
        total_causes = 0
        
        for cat in categories_found:
            causes_list = []
            # Filtrar las filas que corresponden a esta categoría
            group = self.df[self.df["category"] == cat]
            
            for _, row in group.iterrows():
                # Estructura del nodo causa
                item = {"name": row["cause"]}
                
                # Si hay subcausas (porqués), las agregamos como hijos
                if "sub_causes" in row and isinstance(row["sub_causes"], list) and row["sub_causes"]:
                     item["children"] = [{"name": sub} for sub in row["sub_causes"]]
                
                causes_list.append(item)
                total_causes += 1
            
            fishbone_structure[cat] = causes_list

        # 3. Análisis de Balance (Insight cualitativo)
        # Verificamos si el diagrama está desbalanceado (muchas causas en una sola M)
        counts = self.df["category"].value_counts()
        if not counts.empty:
            dominant_cat = counts.idxmax()
            dominant_count = counts.max()
            
            balance_msg = "El análisis cubre múltiples categorías de forma equilibrada."
            # Si una categoría tiene más del 50% de las causas, avisamos
            if dominant_count > (total_causes * 0.5):
                balance_msg = f"Atención: El análisis está sesgado hacia '{dominant_cat}' ({dominant_count} causas)."
        else:
            balance_msg = "No se encontraron categorías válidas."

        summary = (
            f"Diagrama generado con {total_causes} causas potenciales distribuidas en {len(categories_found)} categorías. "
            f"{balance_msg}"
        )

        # 4. Retorno
        # Enviamos la estructura como el primer elemento de chart_data
        return AnalysisResult(
            tool_name="Diagrama de Causa-Efecto (Ishikawa)",
            summary=summary,
            chart_data=[fishbone_structure], 
            details={
                "categories_detected": list(categories_found),
                "cause_distribution": counts.to_dict() if not counts.empty else {}
            }
        )