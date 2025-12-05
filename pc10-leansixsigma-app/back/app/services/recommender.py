# backend/app/services/recommender.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.domain.tools_matrix import TOOLS_DMAIC_MATRIX

class ToolRecommender:
    def __init__(self):
        # 1. Dataset de Entrenamiento (Contexto de cada herramienta)
        # Aquí definimos para qué sirve cada herramienta con palabras clave
        self.knowledge_base = [
            # --- FASE DEFINIR (Enfoque: Alcance y Cliente) ---
            {
                "id": "gantt", 
                "desc": "Cronograma, planificación de proyecto. Caso UAP: Definir fechas objetivo para cada fase del ciclo DMAIC (Definir, Medir, Analizar, Mejorar, Controlar). Project Charter."
            },
            {
                "id": "structure_tree", 
                "desc": "Árbol de estructura, CTQ (Critical to Quality). Caso UAP: Traducir la voz del cliente ('demora en atención') a una métrica técnica específica ('tiempo de atención <= 15 minutos')."
            },
            {
                "id": "process_map", 
                "desc": "Mapa de procesos, Flujograma. Caso UAP: Diagramar el flujo actual (AS-IS) de la matrícula presencial para identificar cuellos de botella y compararlo con el flujo propuesto (TO-BE) vía web."
            },
            {
                "id": "sipoc", 
                "desc": "SIPOC (Supplier-Input-Process-Output-Customer). Caso UAP: Mapeo de alto nivel para identificar proveedores (Alumnos, Bancos), Entradas (Requisitos), y Salidas (Ficha de matrícula)."
            },

            # --- FASE MEDIR (Enfoque: Datos y Línea Base) ---
            {
                "id": "capability", 
                "desc": "Capacidad del proceso, Cp, Cpk, Nivel Sigma. Caso UAP: Medir la capacidad del proceso actual para cumplir con el tiempo de atención de 15 minutos. Determinar que el proceso es incapaz (Z negativo o bajo)."
            },
            {
                "id": "data_collection_plan", 
                "desc": "Plan de recolección de datos. Caso UAP: Definir qué medir (Tiempo de ciclo, % Satisfacción), tipo de dato (continuo/discreto) y tamaño de muestra."
            },
            {
                "id": "gage_rr", 
                "desc": "Gage R&R, MSA. General: Validar que el sistema de medición es confiable antes de recolectar datos masivos."
            },
            {
                "id": "pareto", 
                "desc": "Diagrama de Pareto. Caso UAP/Sysman: Priorizar las causas más frecuentes de quejas o defectos (Regla 80/20). Enfocarse en los 'pocos vitales'."
            },

            # --- FASE ANALIZAR (Enfoque: Causa Raíz) ---
            {
                "id": "ishikawa", 
                "desc": "Diagrama Causa-Efecto, Espina de Pescado. Caso UAP: Analizar por qué la matrícula es lenta. Causas: Mano de Obra (falta capacitación), Métodos (trámites manuales), Maquinaria (sistema lento)."
            },
            {
                "id": "hypothesis", 
                "desc": "Prueba de Hipótesis, T-Test, Proporciones. Caso UAP: Validar estadísticamente si los 'requisitos extracurriculares' son una barrera real para la matrícula web. Comparar medias Antes vs Después."
            },
            {
                "id": "anova", 
                "desc": "ANOVA. Libro Seis Sigma: Comparar si un factor (ej: turno, proveedor) tiene un efecto significativo en el resultado promedio."
            },
            {
                "id": "fmea", 
                "desc": "AMEF, Análisis de Riesgos. Caso UAP: Evaluar riesgos en el nuevo proceso web (ej: caída del servidor) y calcular su NPR para tomar acciones preventivas."
            },
            {
                "id": "interviews", 
                "desc": "Entrevistas, Encuestas. Caso UAP: Recolectar la percepción de los estudiantes sobre por qué no usan la web (Desconfianza, desconocimiento)."
            },

            # --- FASE MEJORAR (Enfoque: Soluciones y Optimización) ---
            {
                "id": "doe", 
                "desc": "Diseño de Experimentos, DOE Factorial. Caso UAP: Determinar qué factores (Publicidad, Inducción, Reglas de Negocio) tienen mayor impacto en aumentar el % de matrícula web."
            },
            {
                "id": "rsm", 
                "desc": "Superficie de Respuesta. General: Encontrar los valores óptimos de operación para maximizar una variable."
            },
            {
                "id": "pmi", 
                "desc": "PMI, Evaluación de soluciones. General: Evaluar los Plus, Minus e Interesante de una propuesta de mejora."
            },
            {
                "id": "raci", 
                "desc": "Matriz RACI. Caso UAP: Definir roles (Responsable, Aprobador, Consultado) para la implementación del nuevo sistema de pagos online."
            },

            # --- FASE CONTROLAR (Enfoque: Sostenibilidad) ---
            {
                "id": "control_plan", 
                "desc": "Plan de Control. Caso UAP: Documento para monitorear el nuevo proceso web. Definir métricas, frecuencias y planes de reacción ante caídas del sistema."
            },
            {
                "id": "spc", 
                "desc": "Gráficos de Control, Cartas P / I-MR. Caso UAP: Monitorear semanalmente el % de matrícula web y el tiempo de ciclo para asegurar que el proceso se mantenga estable."
            },
            {
                "id": "bsc", 
                "desc": "Balanced Scorecard. General: Monitorear indicadores estratégicos de alto nivel a largo plazo."
            },
            
            # --- OTRAS HERRAMIENTAS DE SOPORTE ---
            {"id": "muestreo", "desc": "Cálculo de tamaño de muestra. Caso UAP: Determinar cuántas encuestas hacer para tener 95% de confianza."},
            {"id": "z_bench", "desc": "Nivel Sigma. Caso UAP: Calcular el nivel sigma inicial (0.5) y final (3.0) para demostrar la mejora de calidad."},
            {"id": "cost_benefit", "desc": "Costo Beneficio. Caso UAP: Calcular el ahorro en horas-hombre y papel al migrar a web."},
            {"id": "radar", "desc": "Radar Chart. General: Auditorías 5S y evaluación de competencias."},
            {"id": "scatter", "desc": "Diagrama de dispersión. General: Correlación entre dos variables."},
            {"id": "stratification", "desc": "Estratificación. General: Análisis por grupos."},
            {"id": "run_chart", "desc": "Gráfico de corridas. General: Tendencias simples."},
            {"id": "histogram", "desc": "Histograma. General: Ver distribución de datos."},
            {"id": "conf_interval", "desc": "Intervalo de confianza. General: Estimación de parámetros."},
            {"id": "ce_matrix", "desc": "Matriz Causa Efecto. General: Priorizar entradas."},
            {"id": "qfd", "desc": "QFD. Caso Sysman: Priorizar características técnicas de software."},
            {"id": "affinity", "desc": "Afinidades. General: Agrupar ideas."},
            {"id": "normality", "desc": "Prueba de normalidad. General: Validar datos para estadística."},
            {"id": "chi_square", "desc": "Chi-Cuadrado. General: Independencia de atributos."},
            {"id": "cost_tree", "desc": "Árbol de costos. General: Desglose de costos de calidad."},
            {"id": "boxplot", "desc": "Box Plot. Caso UAP: Comparar dispersión de tiempos Antes vs Después."}
        ]
        
        # Entrenar el vectorizador (Preparamos el cerebro de la IA)
        self.descriptions = [item['desc'] for item in self.knowledge_base]
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.descriptions)

    def recommend(self, phase: str, user_query: str):
        """
        Recomienda herramientas basándose en la fase DMAIC y la descripción del usuario.
        """
        # 1. Filtrar herramientas permitidas por la Fase (Regla de Negocio)
        # Convertimos 'Define' -> 'D', etc.
        phase_map = {
            "Define": "D", "Measure": "M", "Analyze": "A", 
            "Improve": "I", "Control": "C",
            "Definir": "D", "Medir": "M", "Analizar": "A", 
            "Mejorar": "I", "Controlar": "C"
        }
        phase_code = phase_map.get(phase, phase) # Si ya viene como 'D', lo deja así
        
        allowed_tools_ids = [
            t['id'] for t in TOOLS_DMAIC_MATRIX 
            if phase_code in t['phases']
        ]

        # 2. Analizar la consulta del usuario con IA (Similitud Coseno)
        query_vec = self.vectorizer.transform([user_query])
        # Calculamos similitud entre la consulta y TODAS las herramientas
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # 3. Combinar Filtro + IA
        recommendations = []
        for i, score in enumerate(similarities):
            tool_id = self.knowledge_base[i]['id']
            
            # Solo consideramos si la herramienta es válida para esta fase
            if tool_id in allowed_tools_ids:
                # Buscar el nombre bonito
                tool_info = next(t for t in TOOLS_DMAIC_MATRIX if t['id'] == tool_id)
                recommendations.append({
                    "id": tool_id,
                    "name": tool_info['name'],
                    "score": float(score), # Qué tan bien coincide con el texto
                    "reason": self.knowledge_base[i]['desc'] # Por qué se eligió
                })

        # 4. Ordenar por puntuación (Score)
        recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)

        # Devolver top 5
        return recommendations[:5]