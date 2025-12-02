
import pandas as pd
import numpy as np
from scipy import stats
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class SamplingTool(SixSigmaTool):
    def analyze(self) -> AnalysisResult:
        method = self.params.get("method", "calculation")
        
        if method == "calculation":
            return self._calculate_sample_size()
        elif method == "extraction":
            return self._extract_sample()
        else:
            raise ValueError("Método de muestreo no válido")

    def _calculate_sample_size(self) -> AnalysisResult:
        # 1. Obtener parámetros
        conf_level = self.params.get("confidence_level", 0.95)
        margin_error = self.params.get("margin_error", 0.05)
        pop_size = self.params.get("population_size") # N (opcional)
        var_type = self.params.get("variable_type", "attribute")

        # 2. Calcular Z (Valor crítico de la distribución normal)
        # Si conf_level es 0.95, alpha es 0.05, alpha/2 es 0.025. Z es ppf(0.975)
        alpha = 1 - conf_level
        z_score = stats.norm.ppf(1 - alpha/2)

        n = 0
        formula_text = ""

        # 3. Cálculo según el tipo de variable (Libro Pág 103-104)
        if var_type == "attribute":
            # Fórmula para Proporciones (Cualitativa)
            p = self.params.get("proportion", 0.5)
            numerator = (z_score**2) * p * (1 - p)
            denominator = margin_error**2
            n = numerator / denominator
            formula_text = "n = (Z² * p * (1-p)) / E²"
            
        elif var_type == "variable":
            # Fórmula para Medias (Cuantitativa)
            sigma = self.params.get("std_dev")
            if sigma is None:
                raise ValueError("Para variables continuas se requiere una desviación estándar estimada (sigma).")
            
            numerator = (z_score * sigma)**2
            denominator = margin_error**2
            n = numerator / denominator
            formula_text = "n = (Z * σ / E)²"

        # 4. Ajuste por Población Finita (Si N es conocido)
        is_finite = False
        if pop_size and pop_size > 0:
            n = n / (1 + ((n - 1) / pop_size))
            is_finite = True

        final_n = int(np.ceil(n)) # Redondear siempre hacia arriba

        # 5. Respuesta
        summary = (
            f"Para un nivel de confianza del {conf_level*100}% y un error del {margin_error*100}%, "
            f"se requiere un tamaño de muestra de: {final_n} unidades."
        )
        
        if is_finite:
            summary += f" (Ajustado por población finita N={pop_size})"

        return AnalysisResult(
            tool_name="Cálculo de Tamaño de Muestra",
            summary=summary,
            chart_data=[], # No hay gráfico para el cálculo solo
            details={
                "calculated_n": final_n,
                "z_score": round(z_score, 4),
                "formula_used": formula_text,
                "parameters": self.params
            }
        )

    def _extract_sample(self) -> AnalysisResult:
        # Si el usuario subió datos y quiere que el sistema elija por él
        if self.df.empty:
             raise ValueError("Se requieren datos para extraer una muestra.")
        
        # Si el usuario especifica 'n', usamos ese, si no, calculamos uno sugerido
        n_samples = self.params.get("n_samples")
        
        if not n_samples:
            # Autocalcular n basado en parámetros por defecto
            calc_result = self._calculate_sample_size()
            n_samples = calc_result.details["calculated_n"]

        # Validar que no pidamos más datos de los que hay
        total_rows = len(self.df)
        if n_samples > total_rows:
            n_samples = total_rows
            summary = f"La muestra calculada excede los datos. Se devolvieron todas las {total_rows} filas."
        else:
            summary = f"Se han seleccionado aleatoriamente {n_samples} registros de un total de {total_rows}."

        # Extracción aleatoria (Random Sampling) [cite: 5356]
        sample_df = self.df.sample(n=n_samples, random_state=42) # random_state para reproducibilidad
        
        return AnalysisResult(
            tool_name="Extracción de Muestra Aleatoria",
            summary=summary,
            chart_data=sample_df.to_dict(orient='records'),
            details={
                "total_population": total_rows,
                "sample_size": n_samples
            }
        )