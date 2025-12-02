import pandas as pd
from scipy import stats
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class AnovaTool(SixSigmaTool):
    def analyze(self) -> AnalysisResult:
        # 1. Validación de Datos
        if self.df.empty:
            raise ValueError("Se requieren datos para el análisis ANOVA.")

        # Detectar columnas automáticamente: 1 categórica (Grupo) y 1 numérica (Valor)
        try:
            group_col = self.df.select_dtypes(include=['object', 'string']).columns[0]
            value_col = self.df.select_dtypes(include=['number']).columns[0]
        except IndexError:
            raise ValueError("Los datos deben tener al menos una columna de texto (Grupo) y una numérica (Valor).")

        # 2. Preparar los datos para Scipy
        groups = self.df[group_col].unique()
        data_by_group = [self.df[self.df[group_col] == g][value_col].values for g in groups]

        # 3. Cálculo del ANOVA (F_oneway)
        f_statistic, p_value = stats.f_oneway(*data_by_group)

        # 4. Cálculos de la Tabla ANOVA (Para mostrar detalles como en el libro)
        # Grados de libertad
        k = len(groups)  # Número de grupos
        N = len(self.df) # Total de muestras
        df_between = k - 1
        df_within = N - k
        df_total = N - 1

        # Suma de Cuadrados (SS)
        grand_mean = self.df[value_col].mean()
        ss_between = sum([len(g) * (g.mean() - grand_mean)**2 for g in [self.df[self.df[group_col] == g][value_col] for g in groups]])
        ss_total = sum((self.df[value_col] - grand_mean)**2)
        ss_within = ss_total - ss_between

        # Cuadrados Medios (MS)
        ms_between = ss_between / df_between
        ms_within = ss_within / df_within

        # 5. Interpretación Automática
        alpha = 1 - self.params.get("confidence_level", 0.95)
        significant = p_value < alpha
        
        interpretation = "Existe una diferencia estadísticamente significativa entre las medias de los grupos." if significant else "No hay evidencia suficiente para afirmar que las medias son diferentes."
        
        summary = (
            f"Análisis ANOVA para el factor '{group_col}'. "
            f"Valor F = {f_statistic:.2f}, Valor P = {p_value:.4f}. "
            f"Conclusión ({1-alpha:.0%} confianza): {interpretation}"
        )

        # 6. Datos para Gráfico (Boxplot es ideal para ANOVA)
        # Enviamos los datos crudos o pre-procesados para que el frontend dibuje Cajas y Bigotes
        chart_data = []
        for g in groups:
            stats_desc = self.df[self.df[group_col] == g][value_col].describe()
            chart_data.append({
                "group": str(g),
                "min": float(stats_desc['min']),
                "q1": float(stats_desc['25%']),
                "median": float(stats_desc['50%']),
                "q3": float(stats_desc['75%']),
                "max": float(stats_desc['max']),
                "mean": float(stats_desc['mean']),
            })

        return AnalysisResult(
            tool_name="ANOVA de un Factor",
            summary=summary,
            chart_data=chart_data,
            details={
                "anova_table": {
                    "source": ["Tratamiento (Entre)", "Error (Dentro)", "Total"],
                    "df": [df_between, df_within, df_total],
                    "ss": [round(ss_between, 2), round(ss_within, 2), round(ss_total, 2)],
                    "ms": [round(ms_between, 2), round(ms_within, 2), ""],
                    "f": [round(f_statistic, 2), "", ""],
                    "p": [round(p_value, 5), "", ""]
                },
                "is_significant": bool(significant)
            }
        )