# backend/app/tools/gage_rr.py
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import ols
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class GageRRTool(SixSigmaTool):
    """
    Herramienta Gage R&R (Repetibilidad y Reproducibilidad).
    Evalúa si el sistema de medición es confiable.
    Método: ANOVA (Crossed).
    Referencias:
    - Libro Yellow Belt, pág 22 (Herramientas de Medición - Gauge R&R).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren datos de mediciones.")

        required_cols = ["operator", "part", "measurement"]
        self.validate_columns(required_cols)

        # Validar suficiencia de datos
        n_parts = self.df["part"].nunique()
        n_operators = self.df["operator"].nunique()
        
        if n_parts < 2 or n_operators < 2:
            raise ValueError("Se requieren al menos 2 partes y 2 operadores para un estudio R&R válido.")

        # 2. Modelo ANOVA (Measurement ~ Part + Operator + Part:Operator)
        # Convertir categóricas a strings seguros
        self.df["part"] = self.df["part"].astype(str)
        self.df["operator"] = self.df["operator"].astype(str)
        
        try:
            formula = 'measurement ~ C(part) + C(operator) + C(part):C(operator)'
            model = ols(formula, data=self.df).fit()
            anova_table = sm.stats.anova_lm(model, typ=2)

            # Asegurar columna de cuadrados medios (Mean Squares)
            if "mean_sq" not in anova_table.columns:
                anova_table["mean_sq"] = anova_table["sum_sq"] / anova_table["df"]
        except Exception as e:
            raise ValueError(f"Error al calcular ANOVA para Gage R&R: {str(e)}")

        # 3. Extracción de Cuadrados Medios (Mean Squares)
        # Nombres de índices en statsmodels pueden variar, buscamos por substring
        try:
            ms_part = anova_table.filter(like='part', axis=0)['mean_sq'].values[0]
            ms_oper = anova_table.filter(like='operator', axis=0)['mean_sq'].values[0]
            
            # La interacción es el término con ':'
            interaction_row = anova_table[anova_table.index.str.contains(':')]
            ms_interaction = interaction_row['mean_sq'].values[0] if not interaction_row.empty else 0

            # Fila de error (residuales): puede llamarse 'Residual' o estar al final de la tabla
            if 'Residual' in anova_table.index:
                ms_error = anova_table.loc['Residual', 'mean_sq']
            else:
                ms_error = anova_table['mean_sq'].iloc[-1]
        except IndexError:
             raise ValueError("No se pudieron aislar los componentes de varianza. Verifique los datos.")

        # 4. Cálculo de Componentes de Varianza (VarComp)
        # Definir conteos para las fórmulas
        # k = operadores, n = partes, r = repeticiones
        # Asumimos diseño balanceado para simplificar fórmulas estándar
        n_trials = len(self.df) / (n_parts * n_operators)
        
        # Varianza Repetibilidad (Equipment) = MS Error
        var_repeatability = ms_error
        
        # Varianza Interacción (si es negativa, se asume 0)
        var_interaction = max(0, (ms_interaction - ms_error) / n_trials)
        
        # Varianza Reproducibilidad (Appraiser)
        # Var_Oper = (MS_Oper - MS_Interaction) / (Parts * Trials)
        var_reproducibility = max(0, (ms_oper - ms_interaction) / (n_parts * n_trials))
        
        # Gage R&R Total (Measurement System)
        var_gage_rr = var_repeatability + var_reproducibility + var_interaction
        
        # Varianza de Parte (Part-to-Part)
        # Var_Part = (MS_Part - MS_Interaction) / (Operators * Trials)
        var_part = max(0, (ms_part - ms_interaction) / (n_operators * n_trials))
        
        # Varianza Total
        var_total = var_gage_rr + var_part

        # 5. Cálculos de % Estudio (%StudyVar) y Desviación Estándar (SD)
        sigma_mult = self.params.get("sigma_multiplier", 6.0)
        
        metrics = []
        components = {
            "Gage R&R (Total)": var_gage_rr,
            "Repetibilidad (Equipo)": var_repeatability,
            "Reproducibilidad (Operador)": var_reproducibility,
            "Variación Parte-Parte": var_part,
            "Variación Total": var_total
        }

        for name, variance in components.items():
            std_dev = np.sqrt(variance)
            study_var = std_dev * sigma_mult
            pct_study_var = (std_dev / np.sqrt(var_total)) * 100
            
            metrics.append({
                "component": name,
                "variance": round(variance, 4),
                "std_dev": round(std_dev, 4),
                "study_var": round(study_var, 4),
                "pct_study_var": round(pct_study_var, 2)
            })

        # 6. Interpretación (AIAG Standards)
        # %R&R < 10%: Aceptable
        # %R&R 10-30%: Condicional
        # %R&R > 30%: Inaceptable
        pct_grr = metrics[0]["pct_study_var"] # Gage R&R Total %
        
        status = "INACEPTABLE"
        advice = "El sistema de medición debe ser corregido. Demasiada variación en la medición."
        if pct_grr < 10:
            status = "EXCELENTE"
            advice = "El sistema de medición es confiable."
        elif pct_grr < 30:
            status = "CONDICIONAL"
            advice = "El sistema puede ser aceptable dependiendo de la aplicación o costo."

        summary = (
            f"Estudio Gage R&R completado. %R&R Total: {pct_grr}%. "
            f"Estado: {status}. {advice} "
            f"La mayor fuente de variación es '{max(metrics, key=lambda x: x['variance'])['component']}'."
        )

        return AnalysisResult(
            tool_name="Análisis del Sistema de Medición (Gage R&R)",
            summary=summary,
            chart_data=metrics, # Datos para gráfico de barras apiladas
            details={
                "n_parts": n_parts,
                "n_operators": n_operators,
                "n_trials": round(n_trials, 1),
                "anova_results": {
                    "ms_part": round(ms_part, 2),
                    "ms_oper": round(ms_oper, 2),
                    "ms_error": round(ms_error, 2)
                }
            }
        )