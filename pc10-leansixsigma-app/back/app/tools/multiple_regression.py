# backend/app/tools/multiple_regression.py
import pandas as pd
import numpy as np
import statsmodels.api as sm
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class MultipleRegressionTool(SixSigmaTool):
    """
    Herramienta de Regresión Múltiple.
    Modela la relación entre una variable Y y múltiples variables X.
    Referencias:
    - Libro Seis Sigma y sus Aplicaciones, Cap 8 (Regresión).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación y Selección de Datos
        if self.df.empty:
            raise ValueError("Se requieren datos numéricos para la regresión.")

        target_col = self.params.get("target_column")
        if target_col not in self.df.columns:
            raise ValueError(f"La columna objetivo '{target_col}' no existe en los datos.")

        # Identificar predictores (Xs)
        potential_predictors = self.params.get("predictors")
        if not potential_predictors:
            # Usar todas las numéricas excepto el target
            numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
            potential_predictors = [c for c in numeric_cols if c != target_col]

        if not potential_predictors:
             raise ValueError("No se encontraron columnas numéricas para usar como predictores (X).")

        # Limpiar datos (Drop NaNs) para que OLS no falle
        data_clean = self.df[[target_col] + potential_predictors].dropna()
        
        if len(data_clean) < len(potential_predictors) + 2:
             raise ValueError("No hay suficientes datos para el número de variables seleccionadas.")

        Y = data_clean[target_col]
        X = data_clean[potential_predictors]

        # 2. Ajuste del Modelo (OLS)
        # Importante: Statsmodels no agrega intercepto por defecto, hay que hacerlo manual
        X_with_const = sm.add_constant(X)
        model = sm.OLS(Y, X_with_const).fit()

        # 3. Extracción de Resultados
        r_squared = model.rsquared
        adj_r_squared = model.rsquared_adj
        
        coefficients = []
        significant_vars = []
        
        for term in model.params.index:
            coef = model.params[term]
            p_val = model.pvalues[term]
            
            is_sig = p_val < 0.05
            if bool(is_sig) and term != "const":
                significant_vars.append(term)

            coefficients.append({
                "term": term,
                "coefficient": round(coef, 4),
                "std_err": round(model.bse[term], 4),
                "t_value": round(model.tvalues[term], 2),
                "p_value": round(p_val, 5),
                "significant": bool(is_sig)
            })

        # 4. Análisis de Residuos (Predicho vs Real)
        # Esto es vital para validar el modelo visualmente
        data_clean["predicted"] = model.predict(X_with_const)
        data_clean["residual"] = data_clean[target_col] - data_clean["predicted"]
        
        chart_data = data_clean.reset_index().to_dict(orient="records")

        # 5. Generar Resumen
        if significant_vars:
            sig_text = f"Las variables significativas son: {', '.join(significant_vars)}."
        else:
            sig_text = "Ninguna variable parece influir significativamente (P < 0.05)."

        equation = f"{target_col} = {model.params['const']:.2f}"
        for term in significant_vars[:3]: # Mostrar solo primeros 3 en el resumen
            equation += f" + ({model.params[term]:.2f} * {term})"

        summary = (
            f"Modelo de Regresión Ajustado ($R^2$ Adj: {adj_r_squared:.2%}). "
            f"{sig_text} "
            f"Ecuación aprox: {equation}..."
        )

        return AnalysisResult(
            tool_name="Análisis de Regresión Múltiple",
            summary=summary,
            chart_data=chart_data, # Contiene Y real, Y predicha y Residuos
            details={
                "r_squared": r_squared,
                "adj_r_squared": adj_r_squared,
                "f_pvalue": model.f_pvalue,
                "coefficients": coefficients
            }
        )