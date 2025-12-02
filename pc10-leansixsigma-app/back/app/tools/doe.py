import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import ols
from itertools import combinations
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class DoeTool(SixSigmaTool):
    """
    Herramienta de Diseño de Experimentos (DOE).
    Analiza diseños factoriales (2^k) para identificar factores significativos.
    Referencias:
    - Libro Seis Sigma y sus Aplicaciones, Cap 5, Págs 43-45 (Técnica de Yates y ANOVA para Diseño 2^3).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación de Datos
        if self.df.empty:
            raise ValueError("Se requieren datos experimentales para el análisis.")

        # Identificar la variable de respuesta (Y) y los factores (X)
        # Asumimos que la última columna es la respuesta (Y) y las demás son factores
        # o el usuario debe enviar parámetros específicos.
        target_col = self.params.get("response_column")
        if not target_col:
            # Heurística: la última columna numérica es la respuesta
            numeric_cols = self.df.select_dtypes(include=['number']).columns
            target_col = numeric_cols[-1]
        
        factor_cols = [c for c in self.df.columns if c != target_col and c != "run_order"]
        
        if len(factor_cols) < 2:
            raise ValueError("Se requieren al menos 2 factores para un DOE.")

        # 2. Codificación de Factores (-1, +1)
        # Para que los cálculos de efectos sean correctos (ortogonales), 
        # convertimos los valores bajos/altos a -1 y 1.
        df_coded = self.df.copy()
        factor_map = {}
        
        for col in factor_cols:
            # Detectar niveles únicos
            unique_vals = sorted(df_coded[col].unique())
            if len(unique_vals) != 2:
                # Si no es un diseño de 2 niveles, esta lógica simple no aplica directo
                # (Se requeriría lógica para diseños generales, pero nos enfocamos en 2^k)
                raise ValueError(f"El factor '{col}' debe tener exactamente 2 niveles para un análisis 2^k.")
            
            low, high = unique_vals[0], unique_vals[1]
            factor_map[col] = {"low": low, "high": high}
            # Mapear a -1 y 1
            df_coded[col] = df_coded[col].apply(lambda x: -1 if x == low else 1)

        # 3. Construcción del Modelo (Main Effects + Interactions)
        # Fórmula tipo R: "Y ~ A + B + A:B"
        formula_parts = factor_cols.copy()
        
        # Agregar interacciones de 2 vías (A:B, A:C, B:C)
        # Referencia: Libro Seis Sigma, pág 45 (Tabla ANOVA incluye interacciones)
        for comb in combinations(factor_cols, 2):
            formula_parts.append(f"{comb[0]}:{comb[1]}")
            
        formula_str = f"{target_col} ~ {' + '.join(formula_parts)}"

        # 4. Ajuste del Modelo (OLS - Ordinary Least Squares)
        model = ols(formula_str, data=df_coded).fit()
        anova_table = sm.stats.anova_lm(model, typ=2) # Type 2 ANOVA sums of squares

        # 5. Extracción de Resultados (Efectos y P-Values)
        # En diseños codificados (-1, 1), el Efecto = 2 * Coeficiente
        effects_data = []
        summary_significant = []
        
        for term in model.params.index:
            if term == "Intercept":
                continue
                
            coef = model.params[term]
            p_value = model.pvalues[term]
            effect = coef * 2 
            
            # Determinación de significancia (Alpha 0.05 estándar)
            is_significant = p_value < 0.05
            sig_label = "Significativo" if is_significant else "No significativo"
            
            if is_significant:
                summary_significant.append(f"{term}")

            effects_data.append({
                "term": term,
                "effect": float(round(effect, 4)),
                "coefficient": float(round(coef, 4)),
                "p_value": float(round(p_value, 5)),
                "significance": sig_label,
                # Valor absoluto para el diagrama de Pareto
                "abs_effect": abs(effect)
            })

        # Ordenar por impacto absoluto (para Pareto de Efectos)
        effects_data.sort(key=lambda x: x["abs_effect"], reverse=True)

        # 6. Resumen
        if summary_significant:
            summary = (
                f"Análisis DOE ({len(factor_cols)} factores). "
                f"Los factores significativos que afectan a '{target_col}' son: {', '.join(summary_significant)}. "
                f"R-cuadrado del modelo: {model.rsquared:.2%}."
            )
        else:
            summary = f"Análisis DOE completado. No se encontraron factores estadísticamente significativos con los datos actuales (p < 0.05)."

        # 7. Conversión de niveles de factores a tipos nativos de Python (evitar numpy.* en la respuesta)
        factor_levels_py = {}
        for col, levels in factor_map.items():
            low = levels["low"]
            high = levels["high"]
            # Si son numéricos (incluye numpy.number), convertir a float; si no, a str
            if isinstance(low, (int, float, np.number)):
                low_py = float(low)
                high_py = float(high)
            else:
                low_py = str(low)
                high_py = str(high)
            factor_levels_py[col] = {"low": low_py, "high": high_py}

        # 8. Retorno
        return AnalysisResult(
            tool_name="Diseño de Experimentos (DOE Factorial)",
            summary=summary,
            chart_data=effects_data, # Listo para un Gráfico de Pareto de Efectos
            details={
                "r_squared": float(round(model.rsquared, 4)),
                "r_squared_adj": float(round(model.rsquared_adj, 4)),
                "f_statistic": float(round(model.fvalue, 2)),
                "factor_levels": factor_levels_py # Para saber qué era -1 y qué era 1
            }
        )