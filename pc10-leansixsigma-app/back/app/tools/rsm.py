# backend/app/tools/rsm.py
import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.optimize import minimize
from itertools import combinations
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class RsmTool(SixSigmaTool):
    """
    Herramienta de Superficie de Respuesta (RSM).
    Ajusta un modelo cuadrático para encontrar el punto óptimo de operación.
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren datos experimentales.")
        
        target = self.params.get("target_column")
        factors = self.params.get("factors", [])
        goal = self.params.get("goal", "maximize")

        if not target or not factors:
            raise ValueError("Se deben especificar 'target_column' y 'factors'.")
        
        # Validar que existan columnas
        missing = [f for f in factors + [target] if f not in self.df.columns]
        if missing:
            raise ValueError(f"Faltan columnas en los datos: {', '.join(missing)}")

        # 2. Creación de Términos Cuadráticos e Interacciones (Feature Engineering)
        # Para capturar la curvatura, necesitamos X, X^2 y X*Y
        df_model = self.df[factors].copy()
        
        # Términos lineales ya están en df_model
        
        # Términos Cuadráticos (X^2)
        for f in factors:
            df_model[f"{f}^2"] = df_model[f] ** 2
            
        # Términos de Interacción (X*Y)
        for f1, f2 in combinations(factors, 2):
            df_model[f"{f1}*{f2}"] = df_model[f1] * df_model[f2]

        X = sm.add_constant(df_model)
        Y = self.df[target]

        # 3. Ajuste del Modelo Estadístico
        model = sm.OLS(Y, X).fit()
        
        # 4. Búsqueda del Óptimo (Optimización)
        # Definimos una función que predice Y dado un array de factores X
        def predict_y(x_vals):
            # x_vals es un array [val_factor1, val_factor2...]
            # Reconstruimos el diccionario de features como hicimos arriba
            input_dict = {f: val for f, val in zip(factors, x_vals)}
            
            # Construir fila para predicción
            features = [1.0] # Constante
            # Lineales
            for f in factors: features.append(input_dict[f])
            # Cuadráticos
            for f in factors: features.append(input_dict[f]**2)
            # Interacciones
            for f1, f2 in combinations(factors, 2):
                features.append(input_dict[f1] * input_dict[f2])
            
            pred = model.predict([features])[0]
            
            # Scipy minimize siempre minimiza. Si queremos maximizar, invertimos el signo.
            return -pred if goal == "maximize" else pred

        # Definir límites (bounds) basados en los datos reales (no extrapolar demasiado)
        bounds = [(self.df[f].min(), self.df[f].max()) for f in factors]
        
        # Punto de inicio (centro de los datos)
        x0 = [self.df[f].mean() for f in factors]
        
        # Ejecutar optimización
        res = minimize(predict_y, x0, bounds=bounds, method='L-BFGS-B')
        
        optimal_values = dict(zip(factors, res.x))
        predicted_optimum = -res.fun if goal == "maximize" else res.fun

        # 5. Generación de Datos para Gráfico 3D (Solo si hay 2 factores)
        surface_data = []
        if len(factors) == 2:
            f1, f2 = factors
            # Crear una malla (grid) de 20x20 puntos
            x_range = np.linspace(self.df[f1].min(), self.df[f1].max(), 20)
            y_range = np.linspace(self.df[f2].min(), self.df[f2].max(), 20)
            
            for x_val in x_range:
                for y_val in y_range:
                    # Predecir valor Z para cada par (x,y)
                    # Ojo: esto es ineficiente línea a línea, pero claro para entender.
                    # Reusamos la lógica de predicción interna
                    # (En producción, usaríamos vectorización de numpy)
                    pass 
                    # Simulación rápida de predicción para el gráfico:
                    # Z = b0 + b1X + b2Y + ...
                    # Para simplificar el código aquí, devolveremos los coeficientes
                    # y dejamos que el Frontend (React con Plotly) calcule la malla 
                    # usando la ecuación del modelo. Es mucho más rápido transferir 
                    # la ecuación que 400 puntos.
        
        # 6. Resumen
        r2 = model.rsquared
        equation_terms = [f"{round(v,3)}*{k}" for k, v in model.params.items()]
        equation_str = f"{target} = " + " + ".join(equation_terms)
        
        summary = (
            f"Análisis RSM completado ($R^2$={r2:.2%}). "
            f"Valor óptimo estimado de '{target}': {predicted_optimum:.4f}. "
            f"Configuración óptima: {', '.join([f'{k}={v:.2f}' for k,v in optimal_values.items()])}."
        )

        return AnalysisResult(
            tool_name="Superficie de Respuesta (RSM)",
            summary=summary,
            chart_data=[], # El frontend usará los coeficientes para graficar
            details={
                "coefficients": model.params.to_dict(),
                "optimal_settings": optimal_values,
                "predicted_best_y": predicted_optimum,
                "r_squared": r2,
                "equation": equation_str
            }
        )