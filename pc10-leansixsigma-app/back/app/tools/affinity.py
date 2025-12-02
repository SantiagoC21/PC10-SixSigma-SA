# backend/app/tools/affinity.py
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class AffinityTool(SixSigmaTool):
    """
    Herramienta de Diagrama de Afinidades.
    Utiliza Machine Learning (K-Means) para agrupar ideas por similitud de texto.
    Ideal para organizar el caos después de un Brainstorming.
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty or "text" not in self.df.columns:
            raise ValueError("Se requiere una lista de ideas (columna 'text').")

        data = self.df["text"].tolist()
        
        # Necesitamos suficientes datos para agrupar
        if len(data) < 3:
             raise ValueError("Se necesitan al menos 3 ideas para crear afinidades.")

        num_clusters = self.params.get("num_clusters", 3)
        
        # Ajustar clusters si hay pocos datos (no puedes hacer 5 grupos con 4 ideas)
        if len(data) < num_clusters:
            num_clusters = max(2, len(data) // 2)

        # 2. Procesamiento NLP (Vectorización)
        # Convertimos texto a matriz numérica TF-IDF
        # stop_words='english' funciona bien, para español idealmente cargarías una lista
        # Aquí usamos un patrón básico para tokenizar
        vectorizer = TfidfVectorizer(stop_words=None) 
        try:
            X = vectorizer.fit_transform(data)
        except ValueError:
            # Si el texto es muy corto o vacío
            raise ValueError("El texto proporcionado no es suficiente para analizar.")

        # 3. Clustering (K-Means)
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        kmeans.fit(X)
        
        # Asignar el cluster a cada idea
        self.df['cluster_id'] = kmeans.labels_

        # 4. Etiquetado Automático de Grupos
        # Intentamos adivinar el nombre del grupo buscando las palabras más representativas del centroide
        order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names_out()
        
        cluster_names = {}
        for i in range(num_clusters):
            # Tomamos las 2 palabras más importantes del cluster
            top_terms = [terms[ind] for ind in order_centroids[i, :2]]
            cluster_names[i] = "Grupo: " + " & ".join(top_terms).upper()

        self.df['cluster_name'] = self.df['cluster_id'].map(cluster_names)

        # 5. Estructurar Salida
        # Agrupamos para el frontend: { "Grupo A": ["idea 1", "idea 2"], ... }
        groups = {}
        for cluster_name, group_df in self.df.groupby('cluster_name'):
            groups[cluster_name] = group_df['text'].tolist()

        # Convertir a formato de lista para gráficos
        chart_data = []
        for name, items in groups.items():
            chart_data.append({
                "category": name,
                "items": items,
                "count": len(items)
            })

        summary = (
            f"Se han organizado {len(data)} ideas en {num_clusters} grupos de afinidad. "
            f"El grupo más grande es '{max(groups, key=lambda k: len(groups[k]))}'."
        )

        return AnalysisResult(
            tool_name="Diagrama de Afinidades (IA Clustering)",
            summary=summary,
            chart_data=chart_data,
            details={
                "algorithm": "K-Means Clustering + TF-IDF",
                "num_clusters_used": num_clusters
            }
        )