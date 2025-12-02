# backend/app/tools/z_bench.py
import pandas as pd
import numpy as np
from scipy.stats import norm
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class ZBenchTool(SixSigmaTool):
    """
    Herramienta de Cálculo de Z-Bench (Nivel Sigma) y DPMO.
    Convierte la tasa de defectos en una métrica Sigma estandarizada.
    Referencias:
    - Tesis UAP, pág 84 (Cálculo de Z del proceso y DPMO).
    - Libro Seis Sigma y sus Aplicaciones, pág 18-19 (Cálculo de probabilidad Z).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación de Datos
        if self.df.empty:
            raise ValueError("Se requieren datos numéricos para calcular el Z-Bench.")

        num_col = self.df.select_dtypes(include=['number']).columns[0]
        data = self.df[num_col].dropna()
        
        usl = self.params.get("usl")
        lsl = self.params.get("lsl")
        shift = self.params.get("shift", 1.5) # El desplazamiento estándar de 1.5 sigma
        
        if usl is None and lsl is None:
            raise ValueError("Debes especificar al menos un límite (USL o LSL).")

        # 2. Estadísticos del Proceso (Short Term)
        mean = np.mean(data)
        std_dev = np.std(data, ddof=1) # Desviación estándar muestral

        # 3. Cálculo de Probabilidades de Defecto
        prob_below_lsl = 0
        prob_above_usl = 0

        if lsl is not None:
            # Z = (X - Mean) / StdDev
            z_lsl = (lsl - mean) / std_dev
            prob_below_lsl = norm.cdf(z_lsl) # Área a la izquierda

        if usl is not None:
            z_usl = (usl - mean) / std_dev
            prob_above_usl = 1 - norm.cdf(z_usl) # Área a la derecha

        total_defect_rate = prob_below_lsl + prob_above_usl
        
        # Evitar división por cero o log de cero si el proceso es perfecto
        if total_defect_rate == 0:
            total_defect_rate = 1e-9 # Un valor infinitesimal

        # 4. Cálculo de Z-Bench y Métricas
        # Z-Bench es el inverso de la normal para la probabilidad de NO defecto (o defecto, según convención)
        # Usualmente: Z_bench = norm.ppf(1 - total_defect_rate)
        z_bench_st = norm.ppf(1 - total_defect_rate) # Short Term Z
        z_bench_lt = z_bench_st - shift              # Long Term Z (Realidad del cliente)
        
        # DPMO (Defectos por Millón de Oportunidades)
        dpmo = total_defect_rate * 1_000_000
        
        # Yield (Rendimiento)
        yield_percentage = (1 - total_defect_rate) * 100

        # 5. Interpretación (Nivel Sigma)
        # La escala estándar de "Nivel Sigma" suele referirse al Z Short Term (Zst)
        sigma_level = z_bench_st 

        summary = (
            f"El proceso tiene un Nivel Sigma de {sigma_level:.2f} σ. "
            f"Se esperan {dpmo:,.0f} defectos por millón (DPMO). "
            f"El rendimiento (Yield) es del {yield_percentage:.4f}%."
        )

        # 6. Gráfico: Distribución Normal Estándar mostrando el área de defecto
        # Generamos puntos para dibujar la campana
        x_axis = np.linspace(mean - 4*std_dev, mean + 4*std_dev, 100)
        y_axis = norm.pdf(x_axis, mean, std_dev)
        
        chart_data = [{"x": float(x), "y": float(y)} for x, y in zip(x_axis, y_axis)]

        return AnalysisResult(
            tool_name="Z-Bench (Nivel Sigma)",
            summary=summary,
            chart_data=chart_data,
            details={
                "z_bench_st": float(round(z_bench_st, 3)),
                "z_bench_lt": float(round(z_bench_lt, 3)),
                "dpmo": float(round(dpmo, 2)),
                "yield": float(round(yield_percentage, 4)),
                "mean": float(round(mean, 3)),
                "std_dev": float(round(std_dev, 3)),

                "lsl_limit": lsl,
                "usl_limit": usl
            }
        )