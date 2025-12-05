# backend/app/tools/balanced_scorecard.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class BalancedScorecardTool(SixSigmaTool):
    """
    Herramienta Balanced Scorecard (Cuadro de Mando Integral).
    Monitorea el desempeño estratégico en 4 perspectivas.
    Referencias:
    - Kaplan & Norton (Concepto original).
    - Uso en Fase Controlar para sostener métricas de alto nivel.
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren indicadores (KPIs) para el BSC.")

        required_cols = ["perspective", "kpi", "target", "actual"]
        self.validate_columns(required_cols)

        # Default direction si no viene
        if "higher_is_better" not in self.df.columns:
            self.df["higher_is_better"] = True

        # 2. Cálculo de Desempeño (% Cumplimiento)
        results = []
        
        for _, row in self.df.iterrows():
            target = row["target"]
            actual = row["actual"]
            direction = row["higher_is_better"]
            
            # Evitar división por cero
            if target == 0:
                if direction: # Queremos maximizar 0? Raro, pero si actual > 0 es bueno
                    achievement = 100.0 if actual >= 0 else 0.0
                else: # Queremos minimizar (ej: 0 accidentes). Si actual es 0, es 100%
                    achievement = 100.0 if actual == 0 else 0.0
            else:
                if direction:
                    # Más es mejor (Ventas)
                    achievement = (actual / target) * 100
                else:
                    # Menos es mejor (Defectos)
                    # Si mi meta es 10 y tengo 5, cumplí por mucho. 
                    # Fórmula invertida simple: (Target / Actual) * 100 puede dispararse.
                    # Usamos desviación: 100 + (Target - Actual)/Target * 100
                    # Ejemplo: Meta 10, Actual 5. (10-5)/10 = 50% mejor -> 150% cumplimiento
                    achievement = (1 + ((target - actual) / target)) * 100

            # 3. Asignación de Semáforo (RAG Status)
            if achievement >= 100:
                status = "Verde"
            elif achievement >= 90:
                status = "Amarillo"
            else:
                status = "Rojo"

            results.append({
                **row.to_dict(),
                "achievement": round(achievement, 1),
                "status": status
            })

        df_res = pd.DataFrame(results)

        # 4. Agrupación por Perspectiva
        summary_parts = []
        perspective_scores = {}
        
        for persp, group in df_res.groupby("perspective"):
            avg_ach = group["achievement"].mean()
            perspective_scores[persp] = round(avg_ach, 1)
            
            # Estado general de la perspectiva
            health = "Crítico" if avg_ach < 90 else ("Alerta" if avg_ach < 100 else "Saludable")
            summary_parts.append(f"{persp}: {health} ({avg_ach:.0f}%)")

        summary = f"Scorecard Analizado. Estado General: {', '.join(summary_parts)}."

        # 5. Estructura para Frontend
        # El frontend suele mostrar esto en 4 cuadrantes. Enviamos la lista enriquecida.
        chart_data = df_res.to_dict(orient="records")

        return AnalysisResult(
            tool_name="Balanced Scorecard (BSC)",
            summary=summary,
            chart_data=chart_data,
            details={
                "perspective_averages": perspective_scores,
                "total_kpis": len(df_res)
            }
        )