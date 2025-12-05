# backend/app/tools/qfd.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class QfdTool(SixSigmaTool):
    """
    Herramienta QFD (Despliegue de la Función de Calidad) / Casa de la Calidad.
    Prioriza características técnicas (CÓMOs) basadas en necesidades del cliente (QUÉs).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren los requerimientos del cliente (QUÉs).")

        technical_reqs = self.params.get("technical_reqs", [])
        if not technical_reqs:
            raise ValueError("Se debe definir la lista de Requerimientos Técnicos (CÓMOs).")

        # 2. Construcción de la Matriz de Relaciones
        # Filas = Clientes, Columnas = Técnicos
        
        # Extraer pesos del cliente
        customer_weights = self.df.set_index("customer_req")["weight"]
        
        # Crear DataFrame de relaciones llenando con 0 si falta alguna relación
        relationship_data = []
        for _, row in self.df.iterrows():
            rel_map = row["relationships"]
            # Asegurar que el orden coincida con technical_reqs
            row_vals = [rel_map.get(tech, 0) for tech in technical_reqs]
            relationship_data.append(row_vals)
            
        rel_matrix = pd.DataFrame(
            relationship_data, 
            index=self.df["customer_req"], 
            columns=technical_reqs
        )

        # 3. Cálculo de Puntuaciones Técnicas (Producto Punto)
        # Importancia Absoluta = Suma(Peso Cliente * Valor Relación)
        absolute_scores = {}
        
        for tech in technical_reqs:
            # Multiplicamos la columna técnica por el vector de pesos del cliente
            score = (rel_matrix[tech] * customer_weights.values).sum()
            absolute_scores[tech] = int(score)

        # 4. Cálculo de Importancia Relativa (%)
        total_score = sum(absolute_scores.values())
        relative_scores = {}
        if total_score > 0:
            relative_scores = {k: round((v / total_score) * 100, 1) for k, v in absolute_scores.items()}
        else:
            relative_scores = {k: 0 for k in absolute_scores}

        # 5. Ordenamiento (Priorización)
        sorted_techs = sorted(absolute_scores.items(), key=lambda x: x[1], reverse=True)
        top_tech = sorted_techs[0]

        summary = (
            f"Casa de la Calidad analizada. La característica técnica prioritaria es '{top_tech[0]}' "
            f"con un peso absoluto de {top_tech[1]} ({relative_scores[top_tech[0]]}% del impacto total). "
            f"Mejorar esto tendrá el mayor efecto positivo en la satisfacción del cliente."
        )

        # 6. Estructura de Salida
        
        # Datos para Gráfico de Barras (Ranking Técnico)
        chart_data = [
            {
                "technical_req": tech, 
                "absolute_score": score, 
                "relative_score": relative_scores[tech]
            } 
            for tech, score in sorted_techs
        ]
        
        # Datos para visualizar la Matriz (Grid View) en el frontend
        matrix_view = []
        for req_name in rel_matrix.index:
            row_obj = {
                "customer_req": req_name,
                "weight": int(customer_weights[req_name])
            }
            # Agregar las columnas dinámicas de relación
            for tech in technical_reqs:
                row_obj[tech] = int(rel_matrix.at[req_name, tech])
            matrix_view.append(row_obj)

        return AnalysisResult(
            tool_name="QFD (Casa de la Calidad)",
            summary=summary,
            chart_data=chart_data,
            details={
                "matrix_grid": matrix_view,
                "technical_columns": technical_reqs
            }
        )