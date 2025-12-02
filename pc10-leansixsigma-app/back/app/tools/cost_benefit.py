# backend/app/tools/cost_benefit.py
import pandas as pd
import numpy as np
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class CostBenefitTool(SixSigmaTool):
    """
    Herramienta de Análisis Costo-Beneficio.
    Calcula ROI, Beneficio Neto y Punto de Equilibrio (Payback).
    Referencias:
    - Libro Yellow Belt, pág 106 (ROI y Competitividad).
    - Tesis UAP, pág 59 (Justificación económica del proyecto).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren datos de costos y beneficios.")

        required_cols = ["amount", "type", "period"]
        self.validate_columns(required_cols)

        # 2. Organización de Flujos
        # Separar costos y beneficios
        costs = self.df[self.df['type'] == 'cost']
        benefits = self.df[self.df['type'] == 'benefit']

        total_cost = float(costs['amount'].sum())
        total_benefit = float(benefits['amount'].sum())
        net_benefit = float(total_benefit - total_cost)

        # 3. Cálculo del ROI (Retorno de Inversión)
        # Fórmula estándar: (Beneficio Neto / Costo Total) * 100
        if total_cost == 0:
            roi = 0
            roi_text = "Infinito (Sin costos)"
        else:
            roi = (net_benefit / total_cost) * 100
            roi_text = f"{roi:.2f}%"

        # 4. Análisis Temporal (Payback Period)
        # Agrupar por periodo para ver el flujo de caja neto por periodo
        # Asumimos que los costos son negativos y beneficios positivos para el flujo
        self.df['cash_flow'] = self.df.apply(lambda x: -x['amount'] if x['type'] == 'cost' else x['amount'], axis=1)
        
        # Crear una línea de tiempo agregada
        max_period = int(self.df['period'].max())
        
        timeline = pd.DataFrame({'period': range(max_period + 1)})
        
        # Sumar flujos por periodo
        period_flows = self.df.groupby('period')['cash_flow'].sum().reset_index()
        timeline = timeline.merge(period_flows, on='period', how='left').fillna(0)
        
        # Calcular acumulado
        timeline['cumulative'] = timeline['cash_flow'].cumsum()

        # Encontrar el Payback (cuando el acumulado pasa de negativo a positivo)
        payback_period = None
        for i, row in timeline.iterrows():
            if row['cumulative'] >= 0:
                payback_period = row['period']
                break
        
        payback_text = f"en el periodo {payback_period}" if payback_period is not None else "No se recupera la inversión en el tiempo analizado"

        # 5. Resumen
        unit = self.params.get("period_unit", "Meses")
        summary = (
            f"El proyecto tiene un Beneficio Neto de ${net_benefit:,.2f}. "
            f"El ROI estimado es del {roi_text}. "
            f"El punto de equilibrio (Payback) se alcanza {payback_text} ({unit})."
        )

        # 6. Gráfico (Línea de Tendencia de Flujo Acumulado)
        chart_data = []
        for _, row in timeline[['period', 'cumulative', 'cash_flow']].iterrows():
            chart_data.append({
                "period": int(row["period"]),
                "cumulative": float(row["cumulative"]),
                "cash_flow": float(row["cash_flow"]),
            })

        return AnalysisResult(
            tool_name="Análisis Costo-Beneficio (ROI)",
            summary=summary,
            chart_data=chart_data,
            details={
                "total_investment": float(total_cost),
                "total_savings": float(total_benefit),
                "net_value": float(net_benefit),
                "roi_percent": float(roi),
                "payback_period": int(payback_period) if payback_period is not None else None,
            }
        )