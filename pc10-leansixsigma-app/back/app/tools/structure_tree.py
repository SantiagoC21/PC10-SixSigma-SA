# backend/app/tools/structure_tree.py
from typing import Dict, Any, List
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class StructureTreeTool(SixSigmaTool):
    """
    Herramienta de Diagrama de Árbol (Estructura / CTQ).
    Convierte listas planas en jerarquías visuales.
    Referencias:
    - Libro Yellow Belt, pág 92 (Desglose de Trabajo).
    - Tesis UAP, pág 74 (Árbol CTQ).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren datos para construir el árbol.")

        # Normalizar nombres de columnas (si vienen del excel como 'Padre', 'Hijo')
        # Esperamos que el usuario mapee o use: id, label, parent_id
        required_cols = ["id", "label"]
        self.validate_columns(required_cols)

        # Si no existe parent_id, asumimos que es una lista plana (no árbol)
        if "parent_id" not in self.df.columns:
            self.df["parent_id"] = None

        # 2. Lógica de Construcción de Árbol (Algoritmo Recursivo)
        nodes = self.df.to_dict(orient="records")
        tree_map = {node["id"]: {**node, "children": []} for node in nodes}
        roots = []

        for node in nodes:
            node_id = node["id"]
            parent_id = node.get("parent_id")

            # Si tiene padre y el padre existe en el mapa
            if parent_id and parent_id in tree_map:
                # Agregamos este nodo a la lista de hijos del padre
                tree_map[parent_id]["children"].append(tree_map[node_id])
            else:
                # Si no tiene padre (o el padre no está en la lista), es una raíz
                roots.append(tree_map[node_id])

        # 3. Generar Resumen
        total_nodes = len(nodes)
        depth = self._calculate_max_depth(roots)
        root_labels = [r['label'] for r in roots]
        
        summary = (
            f"Se ha estructurado un árbol con {total_nodes} elementos y {depth} niveles de profundidad. "
            f"Nodos raíz detectados: {', '.join(root_labels)}."
        )

        # 4. Retorno
        # Enviamos 'roots' que contiene toda la estructura anidada hacia abajo
        return AnalysisResult(
            tool_name="Diagrama de Árbol (Estructura/CTQ)",
            summary=summary,
            chart_data=roots, 
            details={
                "total_nodes": total_nodes,
                "max_depth": depth,
                "structure_type": self.params.get("type", "General")
            }
        )

    def _calculate_max_depth(self, nodes: List[Dict], current_depth=1):
        """Helper recursivo para saber qué tan profundo es el árbol"""
        if not nodes:
            return current_depth - 1
        
        max_d = current_depth
        for node in nodes:
            if node["children"]:
                d = self._calculate_max_depth(node["children"], current_depth + 1)
                if d > max_d:
                    max_d = d
        return max_d