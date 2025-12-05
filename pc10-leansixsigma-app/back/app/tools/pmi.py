# backend/app/tools/pmi.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class PmiTool(SixSigmaTool):
    """
    Herramienta PMI (Plus, Minus, Interesting).
    Técnica de pensamiento para evaluar una idea desde tres ángulos.
    Calcula un puntaje neto para facilitar la decisión.
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren puntos para el análisis PMI.")

        required_cols = ["text", "type"]
        self.validate_columns(required_cols)

        # Normalizar tipos (Capitalize)
        self.df["type"] = self.df["type"].str.capitalize()
        
        # Asegurar columna de peso
        if "weight" not in self.df.columns:
            self.df["weight"] = 1

        # 2. Agrupación y Cálculos
        # Separamos en 3 dataframes
        plus_df = self.df[self.df["type"] == "Plus"]
        minus_df = self.df[self.df["type"] == "Minus"]
        interesting_df = self.df[self.df["type"] == "Interesting"]

        # Calcular totales
        score_plus = plus_df["weight"].sum()
        score_minus = minus_df["weight"].sum()
        count_interesting = len(interesting_df)

        # Puntaje Neto (Plus - Minus)
        net_score = score_plus - score_minus

        # 3. Decisión Sugerida
        decision = "Indeterminada"
        if net_score > 0:
            strength = "Fuerte" if net_score > 10 else "Leve"
            decision = f"Positiva ({strength})"
        elif net_score < 0:
            strength = "Fuerte" if net_score < -10 else "Leve"
            decision = f"Negativa ({strength})"
        else:
            decision = "Neutral (Empate)"

        # 4. Resumen
        summary = (
            f"Análisis PMI completado. Puntaje Neto: {net_score}. "
            f"Positivos: {score_plus} pts. Negativos: {score_minus} pts. "
            f"Se identificaron {count_interesting} aspectos interesantes a considerar. "
            f"La tendencia de la decisión es: {decision}."
        )

        # 5. Estructura para Frontend (3 Columnas)
        # Devolvemos un objeto con las 3 listas separadas para facilitar el renderizado en columnas
        chart_data = [
            {"category": "Plus", "items": plus_df.to_dict(orient="records"), "total": int(score_plus)},
            {"category": "Minus", "items": minus_df.to_dict(orient="records"), "total": int(score_minus)},
            {"category": "Interesting", "items": interesting_df.to_dict(orient="records"), "total": int(count_interesting)}
        ]

        return AnalysisResult(
            tool_name="PMI (Plus, Minus, Interesting)",
            summary=summary,
            chart_data=chart_data,
            details={
                "net_score": int(net_score),
                "decision_trend": decision
            }
        )