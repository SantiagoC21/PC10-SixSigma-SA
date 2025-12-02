# backend/app/tools/control_charts.py
import pandas as pd
import numpy as np
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class ControlChartTool(SixSigmaTool):
    """
    Herramienta de Control Estadístico de Procesos (SPC).
    Implementa Gráficos X-barra R.
    Referencias:
    - Seis Sigma y sus Aplicaciones, Cap 6, Pág 50 (Fórmulas X-R).
    - Anexo 5 (Tabla de constantes A2, D3, D4).
    """

    # Tabla de constantes (Anexo 5 del libro) para n=2 hasta n=10
    CONSTANTS = {
        2:  {"A2": 1.880, "D3": 0,     "D4": 3.267},
        3:  {"A2": 1.023, "D3": 0,     "D4": 2.574},
        4:  {"A2": 0.729, "D3": 0,     "D4": 2.282},
        5:  {"A2": 0.577, "D3": 0,     "D4": 2.114}, # Valor típico
        6:  {"A2": 0.483, "D3": 0,     "D4": 2.004},
        7:  {"A2": 0.419, "D3": 0.076, "D4": 1.924},
        8:  {"A2": 0.373, "D3": 0.136, "D4": 1.864},
        9:  {"A2": 0.337, "D3": 0.184, "D4": 1.816},
        10: {"A2": 0.308, "D3": 0.223, "D4": 1.777}
    }

    def analyze(self) -> AnalysisResult:
        # 1. Preparación de Datos
        if self.df.empty:
            raise ValueError("Se requieren datos para el gráfico de control.")

        # Detectar si viene una columna con lista de valores o valores planos
        # Asumiremos entrada plana y agruparemos por el tamaño de subgrupo deseado
        num_col = self.df.select_dtypes(include=['number']).columns[0]
        values = self.df[num_col].tolist()
        
        n = self.params.get("subgroup_size", 5) # Default n=5 según mejores prácticas
        
        # Validar n
        if n < 2 or n > 10:
            raise ValueError("Para X-barra R, el tamaño de subgrupo (n) debe estar entre 2 y 10. Para n=1 use I-MR.")

        # Agrupar datos en subgrupos
        # Cortamos los datos que sobren al final si no completan un subgrupo
        num_subgroups = len(values) // n
        if num_subgroups < 2:
             raise ValueError(f"Se necesitan más datos. Con n={n}, solo tienes para {num_subgroups} subgrupo(s). Mínimo 2.")

        subgroups = np.array(values[:num_subgroups * n]).reshape((num_subgroups, n))
        
        # 2. Cálculos Estadísticos por Subgrupo
        means = np.mean(subgroups, axis=1) # X-barra de cada subgrupo
        ranges = np.ptp(subgroups, axis=1) # Rango de cada subgrupo (Max - Min)

        # 3. Cálculos de la Línea Central (Grand Mean)
        x_double_bar = np.mean(means) # Promedio de promedios
        r_bar = np.mean(ranges)       # Promedio de rangos

        # 4. Límites de Control (Fórmulas Libro Pág 50)
        const = self.CONSTANTS.get(n)
        
        # Gráfico R (Rangos)
        ucl_r = const["D4"] * r_bar
        lcl_r = const["D3"] * r_bar # Puede ser 0 para n < 7
        
        # Gráfico X (Promedios)
        ucl_x = x_double_bar + (const["A2"] * r_bar)
        lcl_x = x_double_bar - (const["A2"] * r_bar)

        # 5. Detección de Puntos Fuera de Control (Regla 1: Fuera de límites)
        out_control_x = [i for i, x in enumerate(means) if x > ucl_x or x < lcl_x]
        out_control_r = [i for i, r in enumerate(ranges) if r > ucl_r or r < lcl_r]

        status = "Bajo Control Estadístico"
        if out_control_x or out_control_r:
            status = "FUERA DE CONTROL (Causas Especiales Detectadas)"

        # 6. Preparar Datos para Visualización
        chart_data = []
        for i in range(num_subgroups):
            chart_data.append({
                "subgroup_id": int(i + 1),
                "x_bar": float(round(means[i], 3)),
                "r": float(round(ranges[i], 3)),
                "ucl_x": float(round(ucl_x, 3)),
                "lcl_x": float(round(lcl_x, 3)),
                "center_x": float(round(x_double_bar, 3)),
                "ucl_r": float(round(ucl_r, 3)),
                "lcl_r": float(round(lcl_r, 3)),
                "center_r": float(round(r_bar, 3)),
                "violation": "X" if i in out_control_x else ("R" if i in out_control_r else None),
            })

        summary = (
            f"Gráfico X-Barra R (n={n}). Estado: {status}. "
            f"Promedio Global: {x_double_bar:.3f}. Rango Promedio: {r_bar:.3f}. "
            f"Puntos fuera de control: {len(out_control_x)} en X, {len(out_control_r)} en R."
        )

        return AnalysisResult(
            tool_name="Gráfico de Control X-R (SPC)",
            summary=summary,
            chart_data=chart_data,
            details={
                "constants_used": {k: float(v) for k, v in const.items()},
                "limits": {
                    "x_bar": {"ucl": float(ucl_x), "lcl": float(lcl_x), "cl": float(x_double_bar)},
                    "r": {"ucl": float(ucl_r), "lcl": float(lcl_r), "cl": float(r_bar)},
                }
            }
        )