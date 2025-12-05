# backend/app/tools/run_chart.py
import pandas as pd
import numpy as np
from math import erf
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class RunChartTool(SixSigmaTool):
    """
    Herramienta Gráfico de Series de Tiempo (Run Chart).
    Detecta patrones no aleatorios (Tendencias, Cambios, Ciclos).
    Referencias:
    - Libro Yellow Belt, pág 21 (Monitoreo básico de tendencias).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren datos numéricos ordenados en el tiempo.")

        # Asumimos que la primera columna numérica es el valor (Y)
        # Si hay una de fecha/texto, la usamos como etiqueta (X)
        num_cols = self.df.select_dtypes(include=['number']).columns
        if len(num_cols) == 0:
             raise ValueError("No se encontraron datos numéricos.")
        
        value_col = num_cols[0]
        values = self.df[value_col].values
        
        # Obtener etiquetas de tiempo si existen
        label_col = None
        text_cols = self.df.select_dtypes(include=['object', 'string', 'datetime']).columns
        if len(text_cols) > 0:
            label_col = text_cols[0]

        # 2. Cálculo de Línea Central
        method = self.params.get("center_line", "median")
        if method == "mean":
            center_line = np.mean(values)
        else:
            center_line = np.median(values)

        # 3. Análisis de Corridas (Runs)
        # Un "Run" es una secuencia de puntos consecutivos al mismo lado de la línea central
        # Ignoramos los puntos que caen exactamente en la línea
        diffs = values - center_line
        diffs_no_zeros = diffs[diffs != 0]
        
        if len(diffs_no_zeros) == 0:
             # Caso extremo: todos los datos son iguales a la mediana
             return AnalysisResult(tool_name="Run Chart", summary="Datos constantes.", chart_data=[], details={})

        signs = np.sign(diffs_no_zeros)
        
        # Contar cruces (cuando el signo cambia)
        # Si signo[i] != signo[i+1], hubo un cruce
        crossings = np.sum(signs[:-1] != signs[1:])
        num_runs = crossings + 1
        
        # 4. Detección de Patrones (Rules of Thumb)
        n_useful = len(diffs_no_zeros)
        
        # Regla 1: Shift (Desplazamiento) - 8 puntos consecutivos en un lado
        shifts = 0
        current_run = 1
        for i in range(1, n_useful):
            if signs[i] == signs[i-1]:
                current_run += 1
            else:
                if current_run >= 8: shifts += 1
                current_run = 1
        if current_run >= 8: shifts += 1 # Chequear el último
        
        # Regla 2: Trend (Tendencia) - 6 puntos subiendo o bajando consecutivamente
        trends = 0
        # Calculamos diferencias entre punto y punto (no contra la mediana)
        point_diffs = np.sign(np.diff(values))
        point_diffs = point_diffs[point_diffs != 0] # Ignorar empates
        
        current_trend = 1
        for i in range(1, len(point_diffs)):
            if point_diffs[i] == point_diffs[i-1]:
                current_trend += 1
            else:
                if current_trend >= 6: trends += 1
                current_trend = 1
        if current_trend >= 6: trends += 1

        # 5. Resumen e Interpretación
        # Cálculo de carreras esperadas (para ver si es aleatorio)
        expected_runs = (2 * n_useful - 1) / 3
        std_runs = np.sqrt((16 * n_useful - 29) / 90)
        
        z_runs = (num_runs - expected_runs) / std_runs if std_runs > 0 else 0
        # Aproximación Normal usando función de error de la librería estándar
        p_value_runs = 2 * (1 - 0.5 * (1 + erf(abs(z_runs) / np.sqrt(2))))

        conclusion = "El proceso parece aleatorio."
        if p_value_runs < 0.05:
            if num_runs < expected_runs:
                conclusion = "Posible agrupamiento (Clustering) o desplazamiento de la media."
            else:
                conclusion = "Posible mezcla (Mixture) u oscilación rápida."
        
        if shifts > 0: conclusion += f" Se detectaron {shifts} desplazamientos (Shifts)."
        if trends > 0: conclusion += f" Se detectaron {trends} tendencias fuertes."

        summary = (
            f"Run Chart ({method.title()}={center_line:.2f}). "
            f"Corridas observadas: {num_runs} (Esperadas: {expected_runs:.1f}). "
            f"Valor P (Aleatoriedad): {p_value_runs:.4f}. "
            f"{conclusion}"
        )

        # 6. Datos para Gráfico
        chart_data = []
        for i, val in enumerate(values):
            label = str(self.df.iloc[i][label_col]) if label_col else str(i+1)
            chart_data.append({
                "label": label,
                "value": float(val),
                "center_line": float(center_line)
            })

        return AnalysisResult(
            tool_name="Gráfico de Series de Tiempo (Run Chart)",
            summary=summary,
            chart_data=chart_data,
            details={
                "n_points": len(values),
                "n_runs": int(num_runs),
                "shifts_detected": shifts,
                "trends_detected": trends,
                "p_value_runs": round(p_value_runs, 4)
            }
        )