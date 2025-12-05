# backend/app/tools/pareto_abc.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class ParetoAbcTool(SixSigmaTool):
    """
    Herramienta Diagrama de Pareto y Análisis ABC.
    Prioriza problemas o costos basándose en la regla 80/20.
    Referencias:
    - Libro Seis Sigma y sus Aplicaciones, Cap 5, Pág 35 (Diagrama de Pareto).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren datos para el Pareto.")

        required_cols = ["label", "value"]
        self.validate_columns(required_cols)

        # 2. Procesamiento Matemático
        # Agrupar por si el usuario envió datos repetidos (ej: 3 filas de "Rotura")
        df_grouped = self.df.groupby("label")["value"].sum().reset_index()
        
        # Ordenar descendente (Vital para Pareto)
        df_grouped = df_grouped.sort_values(by="value", ascending=False)
        
        # Calcular métricas acumuladas
        total_val = df_grouped["value"].sum()
        df_grouped["percentage"] = (df_grouped["value"] / total_val) * 100
        df_grouped["cumulative_percentage"] = df_grouped["percentage"].cumsum()

        # 3. Clasificación ABC (Lógica de Negocio)
        limit_a = self.params.get("limit_a", 80)
        limit_b = self.params.get("limit_b", 95)

        def classify_abc(cum_pct):
            # La lógica debe ser inclusiva con el borde inferior
            if cum_pct <= limit_a:
                return "A" # Vital
            elif cum_pct <= limit_b:
                return "B" # Importante
            else:
                return "C" # Trivial

        # Ajuste fino: El primer elemento que cruza el umbral también pertenece a esa clase
        # (Ej: si el acumulado salta de 75% a 85%, ese elemento suele considerarse A)
        # Implementación simplificada vectorizada:
        df_grouped["class"] = df_grouped["cumulative_percentage"].apply(classify_abc)
        
        # Corrección de borde: Si el primero ya pasa el límite (ej un solo defecto es el 90%), es A.
        # La lógica anterior ya lo cubre.

        # 4. Generar Resumen
        count_a = len(df_grouped[df_grouped["class"] == "A"])
        items_a = df_grouped[df_grouped["class"] == "A"]["label"].tolist()
        
        summary = (
            f"Análisis de Pareto/ABC completado. Total analizado: {total_val:,.2f}. "
            f"Se identificaron {count_a} elementos 'Clase A' (Vitales) que representan la mayoría del impacto: {', '.join(items_a[:3])}..."
        )

        # 5. Estructura para Frontend
        # El frontend necesita barras (valor) y línea (porcentaje acumulado)
        # Convertimos todos los valores numéricos a tipos nativos de Python para evitar
        # errores de serialización con Pydantic (numpy.int64, numpy.float64, etc.)
        chart_data = []
        for _, row in df_grouped.iterrows():
            chart_data.append({
                "label": str(row["label"]),
                "value": float(row["value"]),
                "percentage": float(row["percentage"]),
                "cumulative_percentage": float(row["cumulative_percentage"]),
                "class": str(row["class"]),
            })

        abc_dist_raw = df_grouped["class"].value_counts().to_dict()
        abc_distribution = {str(k): int(v) for k, v in abc_dist_raw.items()}

        return AnalysisResult(
            tool_name="Diagrama de Pareto / Análisis ABC",
            summary=summary,
            chart_data=chart_data,
            details={
                "total_value": float(total_val),
                "abc_distribution": abc_distribution,
                "thresholds": {"A": int(limit_a), "B": int(limit_b)}
            }
        )