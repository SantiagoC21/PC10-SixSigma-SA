# backend/app/tools/confidence_interval.py
import pandas as pd
import numpy as np
from scipy import stats
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class ConfidenceIntervalTool(SixSigmaTool):
    """
    Herramienta de Intervalo de Confianza.
    Estima el rango donde se encuentra el parámetro poblacional (Media o Proporción).
    Referencias:
    - Libro Seis Sigma y sus Aplicaciones, Cap 8, Pág 103 (Estimación por Intervalos).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren datos para calcular el intervalo.")

        col_name = self.df.columns[0]
        data = self.df[col_name].dropna()
        
        n = len(data)
        if n < 2:
            raise ValueError("Se requieren al menos 2 datos para calcular un intervalo.")

        conf_level = self.params.get("confidence_level", 0.95)
        var_type = self.params.get("variable_type", "mean")
        target = self.params.get("target_value")
        
        alpha = 1 - conf_level
        
        result_details = {}
        chart_data = []
        summary = ""
        lower_bound = 0.0
        upper_bound = 0.0
        statistic_val = 0.0
        margin_error = 0.0

        # 2. Lógica para MEDIA (Cuantitativa)
        if var_type == "mean":
            # Validar que sean números
            if not np.issubdtype(data.dtype, np.number):
                raise ValueError(f"Para calcular la Media, la columna '{col_name}' debe ser numérica.")
            
            mean = np.mean(data)
            std_dev = np.std(data, ddof=1) # Desviación muestral (s)
            
            statistic_val = mean
            standard_error = std_dev / np.sqrt(n)
            
            # Decisión: Z vs T
            # Si n < 30 usamos T-Student (más conservador), si n >= 30 usamos Normal (Z)
            # El libro menciona T para varianza desconocida (pág 104)
            if n < 30:
                dist_name = "T-Student"
                critical_value = stats.t.ppf(1 - alpha/2, df=n-1)
            else:
                dist_name = "Normal (Z)"
                critical_value = stats.norm.ppf(1 - alpha/2)
                
            margin_error = critical_value * standard_error
            lower_bound = mean - margin_error
            upper_bound = mean + margin_error
            
            summary = (
                f"Intervalo de Confianza para la Media ({conf_level*100}%): [{lower_bound:.4f}, {upper_bound:.4f}]. "
                f"Basado en {n} muestras con media {mean:.4f} y desviación {std_dev:.4f} (Distribución {dist_name})."
            )
            
            result_details = {
                "mean": round(mean, 4),
                "std_dev": round(std_dev, 4),
                "n": n,
                "distribution": dist_name,
                "critical_value": round(critical_value, 4),
                "standard_error": round(standard_error, 4)
            }

        # 3. Lógica para PROPORCIÓN (Cualitativa/Atributos)
        elif var_type == "proportion":
            # Identificar éxito/fracaso
            # Asumimos que el usuario busca la proporción de un valor específico o
            # si son datos binarios (0/1, True/False), calculamos la media.
            
            unique_vals = data.unique()
            if len(unique_vals) > 2:
                # Si hay muchos valores, intentamos binarizar o lanzamos advertencia
                # Por simplicidad, contaremos el valor más frecuente como "éxito" o pediremos param
                # Aquí asumiremos que data es binaria o contamos la ocurrencia del primer valor
                target_category = unique_vals[0] # Tomamos el primero como referencia
                count = (data == target_category).sum()
                p_hat = count / n
                category_label = str(target_category)
            else:
                # Caso ideal binario
                # Si es numérico 0/1, p_hat es la media
                if np.issubdtype(data.dtype, np.number):
                    p_hat = data.mean()
                    category_label = "1 (Éxito)"
                else:
                    target_category = unique_vals[0]
                    count = (data == target_category).sum()
                    p_hat = count / n
                    category_label = str(target_category)

            statistic_val = p_hat
            
            # Aproximación Normal a la Binomial (Wald)
            # Requiere n*p >= 5 y n*(1-p) >= 5 para ser preciso
            critical_value = stats.norm.ppf(1 - alpha/2)
            standard_error = np.sqrt((p_hat * (1 - p_hat)) / n)
            
            margin_error = critical_value * standard_error
            lower_bound = max(0.0, p_hat - margin_error)
            upper_bound = min(1.0, p_hat + margin_error)

            summary = (
                f"Intervalo para la Proporción de '{category_label}' ({conf_level*100}%): [{lower_bound:.2%}, {upper_bound:.2%}]. "
                f"Proporción muestral: {p_hat:.2%} (n={n})."
            )
            
            result_details = {
                "proportion": round(p_hat, 4),
                "category_analyzed": category_label,
                "n": n,
                "method": "Aproximación Normal (Wald)"
            }

        # 4. Análisis contra Objetivo (Target)
        target_analysis = ""
        if target is not None:
            if lower_bound <= target <= upper_bound:
                target_status = "DENTRO"
                target_msg = f"El objetivo {target} está dentro del intervalo, por lo que es estadísticamente posible que la media real sea igual al objetivo."
            else:
                target_status = "FUERA"
                target_msg = f"El objetivo {target} está fuera del intervalo. Hay evidencia significativa de que el proceso no está centrado en el objetivo."
            
            summary += f" {target_msg}"
            result_details["target_status"] = target_status

        # 5. Datos para Gráfico (Visualización de Rango)
        # Formato para un gráfico de barras de error o puntos
        chart_data = [{
            "label": "Estimación",
            "value": statistic_val,
            "min": lower_bound,
            "max": upper_bound,
            "target": target if target is not None else None
        }]

        return AnalysisResult(
            tool_name="Intervalo de Confianza",
            summary=summary,
            chart_data=chart_data,
            details=result_details
        )