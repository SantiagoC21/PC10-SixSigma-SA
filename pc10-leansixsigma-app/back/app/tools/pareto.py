# backend/app/tools/pareto.py
import pandas as pd

from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult


class ParetoTool(SixSigmaTool):
    """Herramienta de diagrama de Pareto sencilla.

    Espera al menos una columna categórica que indique la causa o categoría
    a analizar. Por defecto usará la columna "category", pero se puede
    especificar otra mediante params["category_column"]. Opcionalmente se
    puede usar una columna de conteo/valor (params["value_column"]).
    """

    def analyze(self) -> AnalysisResult:
        if self.df.empty:
            raise ValueError("No se enviaron datos para el análisis de Pareto.")

        category_col = self.params.get("category_column", "category")
        value_col = self.params.get("value_column")

        # Validar columnas necesarias
        required = [category_col]
        if value_col:
            required.append(value_col)

        self.validate_columns(required)

        # 1. Calcular frecuencia o suma por categoría
        if value_col:
            grouped = (
                self.df.groupby(category_col)[value_col]
                .sum()
                .reset_index(name="count")
            )
        else:
            grouped = (
                self.df.groupby(category_col)
                .size()
                .reset_index(name="count")
            )

        if grouped.empty:
            raise ValueError("No se pudieron calcular frecuencias para el Pareto.")

        # 2. Ordenar de mayor a menor
        grouped = grouped.sort_values(by="count", ascending=False)

        # 3. Calcular porcentajes y porcentaje acumulado
        total = grouped["count"].sum()
        grouped["percentage"] = grouped["count"] / total * 100
        grouped["cumulative_percentage"] = grouped["percentage"].cumsum()

        # 4. Preparar resumen
        top_category = grouped.iloc[0][category_col]
        top_contribution = grouped.iloc[0]["percentage"]

        summary = (
            f"Se identificaron {len(grouped)} categorías. "
            f"La categoría principal '{top_category}' representa aproximadamente "
            f"{float(top_contribution):.2f}% del total."
        )

        # 5. Convertir a tipos nativos de Python para evitar problemas de serialización
        chart_data = []
        for _, row in grouped.iterrows():
            chart_data.append({
                category_col: str(row[category_col]),
                "count": int(row["count"]),
                "percentage": float(row["percentage"]),
                "cumulative_percentage": float(row["cumulative_percentage"]),
            })

        return AnalysisResult(
            tool_name="Pareto",
            summary=summary,
            chart_data=chart_data,
            details={
                "total": int(total),
                "categories_count": int(len(grouped)),
                "parameters": self.params,
            },
        )
