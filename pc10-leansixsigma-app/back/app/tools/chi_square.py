# backend/app/tools/chi_square.py
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class ChiSquareTool(SixSigmaTool):
    """
    Herramienta de Prueba de Chi-Cuadrado (Independencia).
    Determina si existe relación significativa entre dos variables categóricas.
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren datos categóricos.")

        row_col = self.params.get("row_column")
        col_col = self.params.get("col_column")
        alpha = self.params.get("alpha", 0.05)

        if not row_col or not col_col:
            raise ValueError("Se deben especificar 'row_column' y 'col_column'.")

        if row_col not in self.df.columns or col_col not in self.df.columns:
            raise ValueError(f"Las columnas '{row_col}' o '{col_col}' no existen en los datos.")

        # 2. Crear Tabla de Contingencia (Crosstab)
        # Cuenta las frecuencias de cada combinación
        contingency_table = pd.crosstab(self.df[row_col], self.df[col_col])

        if contingency_table.empty:
            raise ValueError("No se pudo generar la tabla de contingencia. Verifique los datos.")

        # 3. Cálculo Estadístico (Scipy)
        # chi2: Estadístico calculada
        # p: Valor P
        # dof: Grados de libertad
        # expected: Tabla de frecuencias esperadas (si fueran independientes)
        chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)

        # 4. Interpretación
        is_dependent = p_value < alpha
        
        rel_status = "DEPENDIENTES (Asociadas)" if is_dependent else "INDEPENDIENTES (No relacionadas)"
        conclusion = (
            f"Existe evidencia estadística para afirmar que '{row_col}' y '{col_col}' están relacionadas."
            if is_dependent else
            f"No hay evidencia suficiente para afirmar relación entre '{row_col}' y '{col_col}'."
        )

        summary = (
            f"Prueba Chi-Cuadrado. Valor P: {p_value:.4f}. "
            f"Las variables son estadísticamente {rel_status}. {conclusion}"
        )

        # 5. Estructura de Salida
        # Convertimos la tabla de contingencia a un formato amigable para visualizar (Heatmap)
        matrix_data = []
        for r_name, row in contingency_table.iterrows():
            row_dict = {row_col: str(r_name)}
            for c_name, val in row.items():
                row_dict[str(c_name)] = int(val)
            matrix_data.append(row_dict)

        # Convertir esperados a lista para comparar
        expected_df = pd.DataFrame(expected, index=contingency_table.index, columns=contingency_table.columns)
        expected_data = [] # Similar estructura si se desea mostrar en detalles

        return AnalysisResult(
            tool_name="Prueba de Chi-Cuadrado",
            summary=summary,
            chart_data=matrix_data, # Tabla de frecuencias observadas
            details={
                "chi2_statistic": chi2_stat,
                "p_value": p_value,
                "dof": dof,
                "alpha": alpha,
                "significant": bool(is_dependent),
                "columns_analyzed": [row_col, col_col]
            }
        )