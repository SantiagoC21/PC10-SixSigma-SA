# backend/app/tools/process_map.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class ProcessMapTool(SixSigmaTool):
    def analyze(self) -> AnalysisResult:
        # 1. Validación de Entrada
        if self.df.empty:
            raise ValueError("Se requieren pasos para generar el mapa.")

        required_cols = ["id", "label", "type"]
        self.validate_columns(required_cols)

        # Convertir a lista de diccionarios para trabajar como grafo
        steps = self.df.to_dict(orient="records")
        
        # Crear un mapa de IDs para acceso rápido y validación
        step_map = {s["id"]: s for s in steps}
        all_ids = set(step_map.keys())

        # 2. Análisis de Integridad del Grafo
        warnings = []
        start_nodes = []
        end_nodes = []
        decision_nodes = []
        
        # Contadores de conexiones para detectar huérfanos
        incoming_connections = {id: 0 for id in all_ids}

        for step in steps:
            step_id = step["id"]
            step_type = step["type"]
            next_ids = step.get("next_ids", [])

            # Clasificar nodos
            if step_type == "start": start_nodes.append(step_id)
            if step_type == "end": end_nodes.append(step_id)
            if step_type == "decision": decision_nodes.append(step_id)

            # Validar conexiones salientes
            if step_type == "decision" and len(next_ids) < 2:
                warnings.append(f"La decisión '{step['label']}' debería tener al menos 2 caminos de salida.")
            elif step_type != "end" and len(next_ids) == 0:
                warnings.append(f"El paso '{step['label']}' es un callejón sin salida (no es 'Fin').")

            # Validar destino de conexiones
            for target in next_ids:
                if target not in all_ids:
                    warnings.append(f"El paso '{step['label']}' apunta a un ID inexistente: '{target}'.")
                else:
                    incoming_connections[target] += 1

        # Validar conexiones entrantes (Huérfanos)
        for step_id, count in incoming_connections.items():
            step_type = step_map[step_id]["type"]
            if count == 0 and step_type != "start":
                warnings.append(f"El paso '{step_map[step_id]['label']}' es inalcanzable (nadie conecta con él).")

        # 3. Estadísticas del Proceso
        stats = {
            "total_steps": len(steps),
            "decisions": len(decision_nodes),
            "roles_involved": list(self.df["role"].dropna().unique()) if "role" in self.df.columns else []
        }

        # 4. Resumen
        status_msg = "Flujo validado correctamente." if not warnings else "Se detectaron problemas lógicos."
        summary = (
            f"Mapa de Proceso analizado. Consta de {len(steps)} pasos y {len(decision_nodes)} puntos de decisión. "
            f"{status_msg} { ' '.join(warnings[:3]) }..." # Mostrar solo los primeros errores en el resumen
        )

        # 5. Estructura para Frontend
        # Devolvemos la lista limpia. El frontend (React Flow) usará 'id' y 'next_ids' para dibujar las flechas.
        return AnalysisResult(
            tool_name="Mapa de Procesos",
            summary=summary,
            chart_data=steps,
            details={
                "validation_warnings": warnings,
                "process_stats": stats
            }
        )