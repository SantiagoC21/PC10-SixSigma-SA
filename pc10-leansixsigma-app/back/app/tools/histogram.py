# backend/app/tools/histogram.py
import pandas as pd
import numpy as np
from scipy import stats
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class HistogramTool(SixSigmaTool):
    """
    Herramienta de Histograma y Análisis de Distribución.
    Visualiza la frecuencia de datos y valida si siguen una distribución Normal.
    Referencias:
    - Libro Seis Sigma y sus Aplicaciones, pág 37-38 (Prueba de Normalidad y Figura 6).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren datos numéricos.")

        num_col = self.df.select_dtypes(include=['number']).columns[0]
        data = self.df[num_col].dropna()
        
        if len(data) < 5:
             raise ValueError("Se necesitan al menos 5 datos para un histograma útil.")

        # 2. Estadísticos Descriptivos
        mean = np.mean(data)
        median = np.median(data)
        std_dev = np.std(data, ddof=1)
        skewness = stats.skew(data) # Sesgo (+ Derecha, - Izquierda)
        kurtosis = stats.kurtosis(data) # Curtosis (Pico)

        # 3. Prueba de Normalidad (Shapiro-Wilk para n < 50, D'Agostino para n >= 50)
        # Interpretación: Si P-value > 0.05, asumimos que es Normal.
        if len(data) < 50:
            stat, p_value = stats.shapiro(data)
            test_name = "Shapiro-Wilk"
        else:
            stat, p_value = stats.normaltest(data)
            test_name = "D'Agostino-Pearson"

        is_normal = p_value > 0.05
        dist_type = "Normal (Gaussiana)" if is_normal else "No Normal"

        # 4. Generación de Bins (Barras)
        # Si el usuario no pide bins, numpy decide el mejor método (auto)
        n_bins = self.params.get("bins") or 'auto'
        hist, bin_edges = np.histogram(data, bins=n_bins)

        # Estructurar para el frontend
        chart_data = []
        for i in range(len(hist)):
            chart_data.append({
                "bin_start": float(bin_edges[i]),
                "bin_end": float(bin_edges[i+1]),
                "frequency": int(hist[i]),
                "label": f"{bin_edges[i]:.2f} - {bin_edges[i+1]:.2f}"
            })

        # 5. Resumen e Interpretación
        skew_text = ""
        if abs(skewness) > 0.5:
            skew_text = f"Con sesgo hacia la {'derecha' if skewness > 0 else 'izquierda'}."
        
        summary = (
            f"Análisis de Distribución para '{num_col}'. "
            f"Media: {mean:.2f}, Desviación: {std_dev:.2f}. "
            f"Prueba de {test_name}: P-Value={p_value:.4f}. "
            f"Conclusión: La distribución es {dist_type}. {skew_text}"
        )

        return AnalysisResult(
            tool_name="Histograma y Normalidad",
            summary=summary,
            chart_data=chart_data,
            details={
                "mean": mean,
                "median": median,
                "std_dev": std_dev,
                "skewness": skewness,
                "kurtosis": kurtosis,
                "p_value": p_value,
                "is_normal": bool(is_normal)
            }
        )