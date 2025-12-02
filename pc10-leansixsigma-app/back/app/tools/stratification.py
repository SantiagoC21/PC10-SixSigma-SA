# backend/app/tools/stratification.py
import pandas as pd
import numpy as np
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class StratificationTool(SixSigmaTool):
    """
    Herramienta de Estratificación.
    Separa datos en grupos (estratos) para identificar patrones de variación.
    Referencias:
    - Libro Yellow Belt, pág 36 (Paso 2 de Pareto: Estratificar los datos).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren datos para la estratificación.")

        factor_col = self.params.get("factor_column")
        target_col = self.params.get("target_column")
        metric = self.params.get("metric", "mean")

        if not factor_col or not target_col:
            raise ValueError("Debes especificar 'factor_column' (grupo) y 'target_column' (valor).")

        if factor_col not in self.df.columns or target_col not in self.df.columns:
            raise ValueError(f"Las columnas '{factor_col}' o '{target_col}' no existen en los datos.")

        # 2. Procesamiento (Agrupación)
        # Agrupamos por el factor y calculamos múltiples estadísticas para el target
        try:
            grouped = self.df.groupby(factor_col)[target_col].agg(
                count='count',
                sum='sum',
                mean='mean',
                std='std',
                min='min',
                max='max'
            ).reset_index()
        except Exception as e:
            raise ValueError(f"Error al agrupar datos. Asegúrate que '{target_col}' sea numérica. Detalle: {str(e)}")

        # Rellenar NaN (ej. desviación estándar de un solo dato es NaN)
        grouped = grouped.fillna(0)

        # 3. Ordenamiento
        # Ordenamos por la métrica de interés para facilitar la visualización (como un Pareto)
        if metric in grouped.columns:
            grouped = grouped.sort_values(by=metric, ascending=False)

        # 4. Análisis de Varianza Simple (Insight)
        # Detectar si hay una diferencia grande entre el mejor y el peor grupo
        max_val = grouped[metric].max()
        min_val = grouped[metric].min()
        best_group = grouped.iloc[0][factor_col] # El más alto según el orden
        worst_group = grouped.iloc[-1][factor_col]
        
        # Calcular porcentaje de diferencia
        diff_pct = 0
        if min_val > 0:
            diff_pct = ((max_val - min_val) / min_val) * 100
        
        summary = (
            f"Estratificación por '{factor_col}' completada. "
            f"Se encontraron {len(grouped)} grupos. "
            f"La mayor diferencia en {metric} es del {diff_pct:.1f}% entre '{best_group}' y '{worst_group}'. "
            f"Esto sugiere que el factor '{factor_col}' {'tiene' if diff_pct > 20 else 'tiene poco'} impacto en los resultados."
        )

        # 5. Estructura de Salida
        chart_data = grouped.to_dict(orient="records")

        return AnalysisResult(
            tool_name="Estratificación de Datos",
            summary=summary,
            chart_data=chart_data, # Lista de objetos con todas las estadísticas por grupo
            details={
                "strata_field": factor_col,
                "analyzed_field": target_col,
                "primary_metric": metric
            }
        )