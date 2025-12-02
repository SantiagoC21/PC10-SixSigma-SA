# backend/app/tools/interviews.py
import pandas as pd
import re
from collections import Counter
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class InterviewAnalysisTool(SixSigmaTool):
    """
    Herramienta de Análisis de Entrevistas.
    Procesa transcripciones para identificar frecuencias de palabras y temas comunes.
    Referencias:
    - Tesis UAP, pág 18 (Técnicas e instrumentos: Entrevistas Estructuradas).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requieren registros de entrevistas.")

        required_cols = ["interviewee", "transcript"]
        self.validate_columns(required_cols)

        top_n = self.params.get("top_n_words", 10)
        min_len = self.params.get("min_word_length", 4)

        # 2. Procesamiento de Texto (NLP Básico)
        # Concatenar todo el texto para análisis global
        all_text = " ".join(self.df["transcript"].astype(str).tolist()).lower()
        
        # Limpieza: Quitar signos de puntuación y caracteres especiales
        words = re.findall(r'\w+', all_text)
        
        # Stopwords básicas en español (se podría ampliar o cargar de librería externa)
        stopwords = {
            "para", "como", "pero", "este", "esta", "porque", "cuando", "todo", 
            "estos", "estas", "hay", "que", "los", "las", "una", "uno", "con", 
            "por", "del", "sus", "nos", "más", "muy", "sin", "sobre", "está",
            "son", "tiene", "donde", "hace", "puede", "ser", "eso", "esa"
        }
        
        # Filtrar palabras: longitud mínima y que no sean stopwords
        filtered_words = [w for w in words if len(w) >= min_len and w not in stopwords]

        # 3. Conteo de Frecuencias
        word_counts = Counter(filtered_words).most_common(top_n)

        # 4. Análisis por Entrevistado (Longitud y Riqueza)
        # Calculamos cuántas palabras dijo cada uno para ver quién aportó más info
        self.df["word_count"] = self.df["transcript"].apply(lambda x: len(str(x).split()))
        
        # 5. Generar Resumen
        top_word, top_count = word_counts[0] if word_counts else ("N/A", 0)
        total_interviews = len(self.df)
        
        summary = (
            f"Análisis de {total_interviews} entrevistas completado. "
            f"El tema más recurrente parece ser '{top_word}' (mencionado {top_count} veces). "
            f"Se analizaron un total de {len(filtered_words)} palabras relevantes."
        )

        # 6. Estructura de Salida
        # Gráfico 1: Frecuencia de palabras (Barras)
        chart_data = [{"word": w, "count": c} for w, c in word_counts]
        
        # Detalles: Tabla de participación por usuario
        participation_table = self.df[["interviewee", "date", "word_count"]].to_dict(orient="records")

        return AnalysisResult(
            tool_name="Análisis de Entrevistas (VOC)",
            summary=summary,
            chart_data=chart_data,
            details={
                "participation_stats": participation_table,
                "total_words_processed": len(words)
            }
        )