# backend/app/tools/brainstorming.py
import pandas as pd
from collections import Counter
import re
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class BrainstormingTool(SixSigmaTool):
    """
    Herramienta de Lluvia de Ideas (Brainstorming).
    Agrupa, limpia, prioriza y analiza frecuencias de términos.
    Referencias:
    - Tesis UAP, pág 107 (Generación de Causas Potenciales).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("La lista de ideas está vacía.")

        required_cols = ["text"]
        self.validate_columns(required_cols)
        
        if "votes" not in self.df.columns:
            self.df["votes"] = 1 # Valor por defecto
        else:
            self.df["votes"] = self.df["votes"].fillna(1)


        if "category" not in self.df.columns:
            self.df["category"] = "General"
        else:
            self.df["category"] = self.df["category"].fillna("General")

        # 2. Limpieza y Normalización
        # Convertir a minúsculas y quitar espacios extra para encontrar duplicados
        self.df['clean_text'] = self.df['text'].str.strip().str.lower()
        
        # 3. Agrupación Inteligente (Consolidar Duplicados)
        # Si alguien escribió "Falla motor" y otro "falla motor ", se suman sus votos
        grouped_df = self.df.groupby('clean_text').agg({
            'text': 'first',       # Mantener la primera forma de escritura (la "bonita")
            'votes': 'sum',        # Sumar votos
            'category': 'first'    # Mantener categoría
        }).reset_index(drop=True)

        # 4. Ordenamiento (Priorización)
        grouped_df = grouped_df.sort_values(by='votes', ascending=False)

        # 5. Análisis de Palabras Clave (Para Nube de Palabras / WordCloud)
        # Unimos todo el texto y contamos palabras individuales para ver tendencias
        all_text = " ".join(grouped_df['text'].tolist())
        # Limpieza básica de signos (regex)
        words = re.findall(r'\w+', all_text.lower())
        # Filtrar palabras vacías comunes (stopwords) muy básicas
        stopwords = {'de', 'la', 'el', 'en', 'y', 'a', 'los', 'del', 'las', 'por', 'un', 'para', 'con', 'no', 'si', 'o'}
        filtered_words = [w for w in words if w not in stopwords and len(w) > 2]
        
        word_freq = Counter(filtered_words).most_common(20) # Top 20 palabras

        # 6. Resumen
        top_idea = grouped_df.iloc[0]
        total_votes = int(grouped_df['votes'].sum())

        unique_ideas = len(grouped_df)
        
        summary = (
            f"Se recopilaron {total_votes} votos distribuidos en {unique_ideas} ideas únicas. "
            f"La idea con mayor consenso es '{top_idea['text']}' con {top_idea['votes']} votos."
        )

        # 7. Preparar salida
        # Datos principales: Lista rankeada
        chart_data = []
        for _, row in grouped_df[['text', 'votes', 'category']].iterrows():
            chart_data.append({
                "text": str(row["text"]),
                "votes": int(row["votes"]),
                "category": str(row["category"]),
            })

        # Datos secundarios: Frecuencia de palabras para WordCloud
        word_cloud_data = [{"text": w, "value": c} for w, c in word_freq]

        return AnalysisResult(
            tool_name="Brainstorming (Lluvia de Ideas)",
            summary=summary,
            chart_data=chart_data,
            details={
                "word_cloud": word_cloud_data,
                "total_participation": int(total_votes)
            }
        )