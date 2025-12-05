# backend/app/tools/hypothesis_test.py
import pandas as pd
import numpy as np
from scipy import stats
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class HypothesisTestTool(SixSigmaTool):
    """
    Herramienta de Prueba de Hipótesis (T-Tests).
    Valida si las diferencias entre grupos o contra una meta son reales.
    Referencias:
    - Tesis UAP, pág 221 (Prueba T para comparar medias Antes/Después).
    """

    def analyze(self) -> AnalysisResult:
        if self.df.empty:
            raise ValueError("Se requieren datos para la prueba de hipótesis.")

        test_type = self.params.get("test_type")
        alpha = self.params.get("alpha", 0.05)
        
        stat = 0.0
        p_value = 1.0
        details = {}
        chart_data = []
        summary = ""

        # --- Lógica: 1-Sample T-Test (Comparar media vs Meta) ---
        if test_type == "1_sample":
            target = self.params.get("target_value")
            if target is None:
                raise ValueError("Para 1-Sample T-Test se requiere 'target_value'.")
            
            # Detectar columna numérica
            col = self.params.get("value_column") or self.df.select_dtypes(include=['number']).columns[0]
            data = self.df[col].dropna()
            
            stat, p_value = stats.ttest_1samp(data, target)
            mean = np.mean(data)
            
            details = {"mean": mean, "target": target, "n": len(data)}
            summary = f"Prueba T de 1 Muestra. Media observada: {mean:.2f} vs Meta: {target}."
            
            # Datos para gráfico (Histograma + Línea Meta)
            chart_data = data.to_dict() # Frontend puede hacer un histograma

        # --- Lógica: 2-Sample T-Test (Independientes, ej: A vs B) ---
        elif test_type == "2_sample":
            # Requiere una columna de grupo y una de valor
            group_col = self.params.get("group_column") or self.df.select_dtypes(include=['object', 'string']).columns[0]
            val_col = self.params.get("value_column") or self.df.select_dtypes(include=['number']).columns[0]
            
            groups = self.df[group_col].unique()
            if len(groups) != 2:
                raise ValueError(f"Para 2-Sample T-Test, la columna '{group_col}' debe tener exactamente 2 grupos únicos. Se encontraron: {groups}")
            
            g1_data = self.df[self.df[group_col] == groups[0]][val_col].dropna()
            g2_data = self.df[self.df[group_col] == groups[1]][val_col].dropna()
            
            # Usamos Welch's T-test (equal_var=False) que es más robusto
            stat, p_value = stats.ttest_ind(g1_data, g2_data, equal_var=False)
            
            mean1, mean2 = np.mean(g1_data), np.mean(g2_data)
            details = {
                f"mean_{groups[0]}": mean1, 
                f"mean_{groups[1]}": mean2,
                "diff": mean1 - mean2
            }
            summary = f"Prueba T de 2 Muestras ({groups[0]} vs {groups[1]}). Diferencia de medias: {mean1 - mean2:.2f}."
            
            # Datos para gráfico (Boxplot comparativo)
            chart_data = [
                {"group": str(groups[0]), "values": g1_data.tolist()},
                {"group": str(groups[1]), "values": g2_data.tolist()}
            ]

        # --- Lógica: Paired T-Test (Antes vs Después) ---
        elif test_type == "paired":
            c1 = self.params.get("column_1")
            c2 = self.params.get("column_2")
            
            if not c1 or not c2:
                # Intentar tomar las dos primeras numéricas
                nums = self.df.select_dtypes(include=['number']).columns
                if len(nums) < 2: raise ValueError("Se requieren dos columnas numéricas para prueba pareada.")
                c1, c2 = nums[0], nums[1]
            
            # Datos pareados deben tener mismo tamaño
            data_clean = self.df[[c1, c2]].dropna()
            
            stat, p_value = stats.ttest_rel(data_clean[c1], data_clean[c2])
            
            mean_diff = np.mean(data_clean[c1] - data_clean[c2])
            details = {"mean_diff": mean_diff, "n_pairs": len(data_clean)}
            summary = f"Prueba T Pareada ({c1} vs {c2}). Diferencia promedio: {mean_diff:.2f}."
            
            chart_data = [{"pair_id": i, "diff": val} for i, val in enumerate(data_clean[c1] - data_clean[c2])]

        else:
            raise ValueError("Tipo de prueba no válido.")

        # --- Interpretación Final ---
        is_significant = p_value < alpha
        decision = "RECHAZAR la Hipótesis Nula (H0)" if is_significant else "NO RECHAZAR la Hipótesis Nula (H0)"
        conclusion = "Existe una diferencia estadísticamente significativa." if is_significant else "No hay evidencia suficiente para afirmar que son diferentes."
        
        full_summary = f"{summary} Valor P: {p_value:.5f}. Decisión: {decision}. Conclusión: {conclusion}"

        return AnalysisResult(
            tool_name=f"Prueba de Hipótesis ({test_type})",
            summary=full_summary,
            chart_data=chart_data,
            details={
                **details,
                "t_statistic": round(stat, 4),
                "p_value": p_value,
                "alpha": alpha,
                "significant": bool(is_significant)
            }
        )