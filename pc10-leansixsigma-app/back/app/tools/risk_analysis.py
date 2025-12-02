# backend/app/tools/risk_analysis.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult, RiskRow

class RiskAnalysisTool(SixSigmaTool):
    def analyze(self) -> AnalysisResult:
        # 1. Validación de Estructura
        if self.df.empty:
            raise ValueError("No se enviaron datos para el análisis de riesgos.")
            
        required_cols = ["severity", "occurrence", "detection"]
        self.validate_columns(required_cols)

        # 2. Cálculos Matemáticos (Quantitative)
        # Cálculo del Número Prioritario de Riesgo (NPR)
        self.df['npr'] = self.df['severity'] * self.df['occurrence'] * self.df['detection']
        
        # Cálculo de Criticidad (Severidad x Ocurrencia)
        # Según Tabla 29 del Libro Yellow Belt 
        self.df['criticality'] = self.df['severity'] * self.df['occurrence']

        # 3. Clasificación de Riesgo (Lógica de Negocio)
        # Definimos niveles basados en la práctica estándar de Six Sigma
        def classify_risk(row):
            if row['npr'] >= 200:
                return "Crítico (Acción Inmediata)"
            elif row['npr'] >= 100:
                return "Alto (Atención Requerida)"
            elif row['npr'] >= 50:
                return "Medio"
            else:
                return "Bajo"

        self.df['risk_level'] = self.df.apply(classify_risk, axis=1)

        # 4. Ordenamiento (Pareto de Riesgos)
        # Ordenamos descendente por NPR para mostrar lo más urgente arriba [cite: 3132]
        self.df = self.df.sort_values(by='npr', ascending=False)

        # 5. Generación de Insights (Qualitative)
        top_risk = self.df.iloc[0]
        total_risks = len(self.df)
        high_risks = len(self.df[self.df['npr'] >= 100])

        summary = (
            f"Se han analizado {total_risks} modos de falla potenciales. "
            f"Se detectaron {high_risks} riesgos de prioridad Alta/Crítica. "
            f"El riesgo prioritario es '{top_risk.get('failure_mode', 'N/A')}' "
            f"con un NPR de {top_risk['npr']} y una criticidad de {top_risk['criticality']}."
        )

        # 6. Estructurar Datos para Gráficos (Matriz de Criticidad)
        # Preparamos datos para un gráfico de dispersión (Scatter Plot)
        # Eje X: Ocurrencia, Eje Y: Severidad, Tamaño: NPR
        chart_data = self.df.to_dict(orient='records')

        return AnalysisResult(
            tool_name="Análisis de Riesgos (AMEF)",
            summary=summary,
            chart_data=chart_data,
            details={
                "max_npr": int(self.df['npr'].max()),
                "avg_npr": float(self.df['npr'].mean()),
                "critical_items_count": high_risks
            }
        )