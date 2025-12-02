# backend/app/tools/radar.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class RadarTool(SixSigmaTool):
    """
    Herramienta de Diagrama de Radar (Gap Analysis).
    Ideal para auditorías 5S, matrices de habilidades y benchmarking.
    Referencias:
    - Libro Yellow Belt, pág 119 (Auditorías 5S y visualización de desempeño).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren datos para el radar.")

        required_cols = ["category", "value"]
        self.validate_columns(required_cols)

        if "series" not in self.df.columns:
            self.df["series"] = "Serie 1"

        # 2. Normalización y Pivot
        # Necesitamos asegurar que todas las series tengan todas las categorías
        categories = self.df["category"].unique()
        series_names = self.df["series"].unique()
        
        # Crear un DataFrame pivoteado: Filas=Categorías, Columnas=Series
        # Esto facilita mucho el cálculo de diferencias
        pivot_df = self.df.pivot_table(index="category", columns="series", values="value", fill_value=0)

        # 3. Cálculos de Análisis (Gaps)
        # Si hay exactamente 2 series, calculamos la brecha automáticamente
        gap_analysis = ""
        if len(series_names) == 2:
            s1, s2 = series_names[0], series_names[1]
            # Calcular diferencia absoluta
            pivot_df["diff"] = pivot_df[s1] - pivot_df[s2]
            pivot_df["abs_diff"] = pivot_df["diff"].abs()
            
            # Encontrar la mayor brecha
            max_gap_cat = pivot_df["abs_diff"].idxmax()
            max_gap_val = pivot_df.loc[max_gap_cat, "abs_diff"]
            
            gap_analysis = (
                f"Comparando '{s1}' vs '{s2}'. "
                f"La mayor brecha se encuentra en '{max_gap_cat}' con una diferencia de {max_gap_val:.2f}."
            )
        else:
            # Análisis general
            best_cat = self.df.groupby("category")["value"].mean().idxmax()
            worst_cat = self.df.groupby("category")["value"].mean().idxmin()
            gap_analysis = f"El área más fuerte es '{best_cat}' y la más débil es '{worst_cat}'."

        # 4. Preparar Datos para Frontend (Formato estándar de gráficos de radar)
        # Transformamos el pivot de vuelta a una lista de diccionarios:
        # [{ "category": "5S", "Serie A": 4, "Serie B": 5 }, ...]
        chart_data = pivot_df.drop(columns=["diff", "abs_diff"], errors="ignore").reset_index().to_dict(orient="records")

        # Calcular escala automática si no se provee
        max_val = self.df["value"].max()
        suggested_scale = self.params.get("max_scale") or (max_val * 1.1)

        summary = (
            f"Análisis de Radar con {len(categories)} ejes y {len(series_names)} series. "
            f"{gap_analysis}"
        )

        return AnalysisResult(
            tool_name="Diagrama de Radar",
            summary=summary,
            chart_data=chart_data,
            details={
                "series_names": list(series_names),
                "categories": list(categories),
                "suggested_max_scale": suggested_scale
            }
        )