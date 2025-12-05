# backend/app/tools/control_plan.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class ControlPlanTool(SixSigmaTool):
    """
    Herramienta Plan de Control.
    Estandariza cómo se monitoreará el proceso post-mejora.
    Referencias:
    - Tesis UAP, pág 197 (Fase Controlar: Plan de Control).
    - Libro Seis Sigma y sus Aplicaciones, pág 48 (Etapa de Control).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación de Datos
        if self.df.empty:
            raise ValueError("El Plan de Control está vacío.")

        required_cols = ["process_step", "characteristic", "control_method", "reaction_plan"]
        self.validate_columns(required_cols)

        # 2. Análisis de Calidad del Plan
        warnings = []
        
        # Regla: Todo control debe tener un plan de reacción
        missing_reaction = self.df[
            (self.df["control_method"].notna()) & 
            (self.df["reaction_plan"].isna() | (self.df["reaction_plan"] == ""))
        ]
        
        if not missing_reaction.empty:
            steps = ", ".join(missing_reaction["process_step"].tolist())
            warnings.append(f"Alerta: Los pasos '{steps}' tienen método de control pero NO tienen Plan de Reacción definido.")

        # Regla: Distinguir controles preventivos vs detectivos
        # Heurística simple buscando palabras clave
        preventive_keywords = ["poka yoke", "automático", "sensor", "diseño", "preventivo"]
        self.df["type"] = self.df["control_method"].apply(
            lambda x: "Preventivo" if any(k in str(x).lower() for k in preventive_keywords) else "Detectivo"
        )
        
        # 3. Estadísticas del Plan
        total_points = len(self.df)
        preventive_count = len(self.df[self.df["type"] == "Preventivo"])
        detective_count = total_points - preventive_count
        
        responsibles = self.df["responsible"].nunique()

        # 4. Resumen
        status = "El plan es robusto." if not warnings else "El plan requiere atención."
        summary = (
            f"Plan de Control generado con {total_points} puntos de control. "
            f"Estrategia: {preventive_count} controles preventivos y {detective_count} detectivos. "
            f"Involucra a {responsibles} roles responsables. {status}"
        )
        if warnings:
            summary += " " + " ".join(warnings)

        # 5. Estructura de Salida
        chart_data = self.df.to_dict(orient="records")

        return AnalysisResult(
            tool_name="Plan de Control",
            summary=summary,
            chart_data=chart_data,
            details={
                "preventive_ratio": round(preventive_count / total_points * 100, 1),
                "warnings": warnings
            }
        )