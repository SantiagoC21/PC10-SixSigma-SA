# backend/app/tools/boxplot.py
import pandas as pd
import numpy as np
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class BoxPlotTool(SixSigmaTool):
    """
    Herramienta de Diagrama de Caja (Box Plot).
    Calcula cuartiles, bigotes y detecta outliers para comparar distribuciones.
    Referencias:
    - Libro Lean Six Sigma Yellow Belt, pág 22 (Herramientas de Análisis).
    - Tesis UAP, pág 228 (Uso para comparar tiempos de registro).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación de Datos
        if self.df.empty:
            raise ValueError("Se requieren datos numéricos para el Box Plot.")

        # Identificar columnas: 
        # - Numérica (Obligatoria): Los valores a medir (ej. Tiempo)
        # - Categórica (Opcional): Para agrupar (ej. Antes vs Después, Maquina A vs B)
        num_col = self.df.select_dtypes(include=['number']).columns
        if len(num_col) == 0:
            raise ValueError("No se encontró ninguna columna numérica.")
        value_col = num_col[0]

        cat_col = self.df.select_dtypes(include=['object', 'string', 'category']).columns
        group_col = cat_col[0] if len(cat_col) > 0 else None

        # 2. Procesamiento por Grupo
        chart_data = []
        
        # Si no hay grupo, creamos uno ficticio "General"
        groups = [( "General", self.df )]
        if group_col:
            groups = list(self.df.groupby(group_col))

        summary_parts = []

        for name, group_df in groups:
            values = group_df[value_col].dropna()
            if values.empty:
                continue

            # 3. Cálculos Estadísticos (Los 5 números de Tukey)
            q1 = np.percentile(values, 25)
            median = np.percentile(values, 50)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            
            # Límites para bigotes (Whiskers) - 1.5 * IQR
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            # Encontrar los valores adyacentes (los bigotes reales no exceden los datos)
            # Bigote inferior: el valor más bajo dentro del límite
            whisker_min = values[values >= lower_bound].min()
            # Bigote superior: el valor más alto dentro del límite
            whisker_max = values[values <= upper_bound].max()
            
            # Si no hay datos dentro del rango (caso raro), ajustamos a cuartiles
            if np.isnan(whisker_min): whisker_min = q1
            if np.isnan(whisker_max): whisker_max = q3

            # 4. Detección de Outliers
            outliers = values[(values < lower_bound) | (values > upper_bound)].tolist()

            # Asegurar que los outliers sean floats nativos
            outliers_py = [float(o) for o in outliers]

            # Guardar datos estructurados para el gráfico
            chart_data.append({
                "category": str(name),
                "min": float(whisker_min),
                "q1": float(q1),
                "median": float(median),
                "q3": float(q3),
                "max": float(whisker_max),
                "outliers": outliers_py,
            })
            
            summary_parts.append(f"{name}: Mediana={float(median):.2f}, Rango={float(whisker_max-whisker_min):.2f}")

        # 5. Resumen
        summary = f"Análisis de dispersión para '{value_col}'. " + " | ".join(summary_parts) + "."

        return AnalysisResult(
            tool_name="Diagrama de Caja (Box Plot)",
            summary=summary,
            chart_data=chart_data,
            details={
                "variable_analizada": value_col,
                "agrupado_por": group_col if group_col else "Sin grupo"
            }
        )