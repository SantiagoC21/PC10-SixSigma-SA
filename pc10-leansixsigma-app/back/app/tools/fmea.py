# backend/app/tools/fmea.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class FmeaTool(SixSigmaTool):
    """
    Herramienta AMEF / FMEA (Análisis de Modo y Efecto de Falla).
    Calcula el NPR para priorizar riesgos en procesos o diseños.
    Referencias:
    - Libro Seis Sigma y sus Aplicaciones, Cuadro 12 (Pág 24).
    - Caso Sysman, Pág 58 (Cálculo NPR = S * O * D).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación de Datos
        if self.df.empty:
            raise ValueError("La tabla AMEF está vacía.")

        required_cols = ["function_part", "failure_mode", "severity", "occurrence", "detection"]
        self.validate_columns(required_cols)

        # 2. Cálculo del NPR (Número Prioritario de Riesgo)
        # Fórmula: NPR = Severidad * Ocurrencia * Detección
        self.df["npr"] = self.df["severity"] * self.df["occurrence"] * self.df["detection"]

        # 3. Clasificación de Riesgo (Lógica de Negocio)
        # Umbrales típicos en industria: >100 Alto, >200 Crítico
        def get_risk_category(val):
            if val >= 200: return "Crítico"
            if val >= 100: return "Alto"
            if val >= 50: return "Medio"
            return "Bajo"

        self.df["risk_category"] = self.df["npr"].apply(get_risk_category)

        # 4. Ordenamiento (Priorización)
        # El objetivo del AMEF es atacar primero los NPR más altos
        self.df = self.df.sort_values(by="npr", ascending=False)

        # 5. Generar Resumen
        top_failure = self.df.iloc[0]
        total_items = len(self.df)
        critical_items = len(self.df[self.df["npr"] >= 100])

        summary = (
            f"Análisis AMEF completado con {total_items} modos de falla. "
            f"Se encontraron {critical_items} fallas de riesgo Alto/Crítico. "
            f"La prioridad #1 es '{top_failure['failure_mode']}' (Causa: {top_failure['cause']}) "
            f"con un NPR de {top_failure['npr']}."
        )

        # 6. Estructura de Salida
        # Devolvemos la tabla completa ordenada para que el frontend la muestre como reporte
        chart_data = self.df.to_dict(orient="records")

        return AnalysisResult(
            tool_name="AMEF (Análisis de Modo y Efecto de Falla)",
            summary=summary,
            chart_data=chart_data,
            details={
                "max_npr": int(self.df["npr"].max()),
                "total_risk_sum": int(self.df["npr"].sum()),
                "critical_count": critical_items
            }
        )