# backend/app/tools/normality_test.py
import pandas as pd
import numpy as np
from scipy import stats
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class NormalityTestTool(SixSigmaTool):
    """
    Herramienta de Prueba de Normalidad y Gráfico de Probabilidad (Q-Q Plot).
    Valida rigurosamente si los datos siguen una distribución Normal.
    Referencias:
    - Libro Seis Sigma y sus Aplicaciones, pág 38 (Gráfica de Probabilidad Normal).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren datos numéricos.")

        col_name = self.df.select_dtypes(include=['number']).columns[0]
        data = self.df[col_name].dropna().values
        n = len(data)

        if n < 3:
            raise ValueError("Se necesitan al menos 3 datos para una prueba de normalidad.")

        alpha = self.params.get("alpha", 0.05)
        
        # 2. Pruebas Estadísticas
        # Shapiro-Wilk (Mejor para n < 50)
        shapiro_stat, shapiro_p = stats.shapiro(data)
        
        # Anderson-Darling (Más robusto en las colas, estándar en Six Sigma)
        anderson_res = stats.anderson(data, dist='norm')
        anderson_stat = anderson_res.statistic
        # Scipy devuelve valores críticos para alphas específicos. 
        # Estimamos P-Value aproximado o comparamos con crítico al 5%
        # Critical values index: 2 correspond to 5% significance level usually
        critical_val_5pct = anderson_res.critical_values[2] 
        is_normal_ad = anderson_stat < critical_val_5pct

        # Decisión final (Usando P-Value de Shapiro como referencia principal numérica)
        p_value_display = shapiro_p
        is_normal = p_value_display > alpha

        # 3. Generación de Datos para Gráfico Q-Q (Probability Plot)
        # Ordenar datos reales
        sorted_data = np.sort(data)
        
        # Calcular cuantiles teóricos (Z-scores esperados)
        # Fórmula de Filliben (o similar) para la posición de ploteo: (i - 0.5) / n
        plotting_positions = (np.arange(1, n + 1) - 0.5) / n
        theoretical_quantiles = stats.norm.ppf(plotting_positions)

        # Línea de referencia (Ajuste lineal de los datos ideales)
        # Pendiente = Desviación Estándar, Intercepto = Media
        mean = np.mean(data)
        std_dev = np.std(data, ddof=1)
        
        # Generar puntos para la línea roja de referencia
        line_x = [min(theoretical_quantiles), max(theoretical_quantiles)]
        line_y = [mean + (x * std_dev) for x in line_x]

        # Estructurar datos para el gráfico
        # Eje X: Cuantiles Teóricos (Desviaciones Estándar)
        # Eje Y: Datos Reales
        qq_data = []
        for i in range(n):
            qq_data.append({
                "theoretical_quantile": float(theoretical_quantiles[i]), # Eje X
                "observed_value": float(sorted_data[i])                  # Eje Y
            })

        # 4. Resumen
        conclusion = "Los datos siguen una distribución Normal." if is_normal else "Los datos NO siguen una distribución Normal."
        summary = (
            f"Prueba de Normalidad para '{col_name}'. "
            f"Anderson-Darling: {anderson_stat:.3f}. Valor P (Shapiro): {p_value_display:.4f}. "
            f"Conclusión (al { (1-alpha)*100 }%): {conclusion}"
        )

        return AnalysisResult(
            tool_name="Prueba de Normalidad (Q-Q Plot)",
            summary=summary,
            chart_data=[{
                "points": qq_data,
                "reference_line": [{"x": line_x[0], "y": line_y[0]}, {"x": line_x[1], "y": line_y[1]}]
            }],
            details={
                "mean": mean,
                "std_dev": std_dev,
                "shapiro_p_value": p_value_display,
                "anderson_statistic": anderson_stat,
                "n_samples": n,
                "is_normal": bool(is_normal)
            }
        )


