# backend/app/tools/cost_tree.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class CostTreeTool(SixSigmaTool):
    """
    Herramienta de Árbol de Costos de Calidad (COPQ).
    Clasifica costos en: Prevención, Evaluación, Fallas Internas, Fallas Externas.
    Referencias:
    - Six Sigma Mejora Procesos Matricula UAP, pág 64 (Costo de mala calidad).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requiere una lista de costos para generar el árbol.")

        required_cols = ["description", "amount", "category"]
        self.validate_columns(required_cols)

        # 2. Cálculos de Agrupación
        # Agrupar por categoría para obtener subtotales
        category_totals = self.df.groupby("category")["amount"].sum().to_dict()

        # Convertir a tipos nativos float
        category_totals_py = {k: float(v) for k, v in category_totals.items()}
        
        # Totales Generales
        total_quality_cost = float(self.df["amount"].sum())
        
        # Calcular COPQ (Cost of Poor Quality) = Fallas Internas + Externas
        copq = float(category_totals_py.get("falla_interna", 0.0) + category_totals_py.get("falla_externa", 0.0))
        
        # Calcular CoGQ (Cost of Good Quality) = Prevención + Evaluación
        cogq = float(category_totals_py.get("prevencion", 0.0) + category_totals_py.get("evaluacion", 0.0))

        # 3. Análisis de Impacto (Si se proveen ingresos)
        revenue = self.params.get("total_revenue")
        impact_text = ""
        if revenue and revenue > 0:
            percent_revenue = (total_quality_cost / revenue) * 100
            impact_text = f" Los costos de calidad representan el {percent_revenue:.2f}% de los ingresos totales."

        # 4. Estructura de Árbol (Para gráficos tipo Treemap/Sunburst en Frontend)
        # Estructura: Root -> Categoría -> Items
        tree_structure = {
            "name": "Costo Total de Calidad",
            "value": total_quality_cost,
            "children": []
        }

        # Mapeo de nombres legibles para la gráfica
        cat_names = {
            "prevencion": "Prevención (Inversión)",
            "evaluacion": "Evaluación (Inspección)",
            "falla_interna": "Fallas Internas (Desperdicio)",
            "falla_externa": "Fallas Externas (Daño al Cliente)"
        }

        for cat, group in self.df.groupby("category"):
            children_items = group[["description", "amount"]].rename(columns={"description": "name", "amount": "value"}).to_dict(orient="records")
            tree_structure["children"].append({
                "name": cat_names.get(cat, cat),
                "value": float(group["amount"].sum()),
                "children": children_items
            })

        # 5. Resumen Automático
        summary = (
            f"El Costo Total de Calidad es ${total_quality_cost:,.2f}. "
            f"El COPQ (Mala Calidad) es ${copq:,.2f} ({(copq/total_quality_cost)*100:.1f}% del total). "
            f"Se está invirtiendo ${cogq:,.2f} en Buena Calidad.{impact_text}"
        )

        return AnalysisResult(
            tool_name="Árbol de Costos de Calidad",
            summary=summary,
            chart_data=[tree_structure], # Enviamos el árbol completo como un solo objeto en la lista
            details={
                "total_copq": float(copq),
                "total_cogq": float(cogq),
                "breakdown": category_totals_py
            }
        )