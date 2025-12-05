
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pydantic import Field
from typing import Literal
from enum import Enum

class AnalysisRequest(BaseModel):
    tool_name: str              
    data: List[Dict[str, Any]]  
    parameters: Optional[Dict[str, Any]] = {} 

class AnalysisResult(BaseModel):
    tool_name: str
    summary: str                
    chart_data: List[Dict[str, Any]] 
    details: Dict[str, Any]     
    status: str = "success"

class SamplingParams(BaseModel):
    method: Literal["calculation", "extraction"] = "calculation"
    variable_type: Literal["attribute", "variable"] = "attribute" 
    confidence_level: float = Field(0.95, ge=0.80, le=0.999) 
    margin_error: float = Field(0.05, gt=0) 
    population_size: Optional[int] = None 
    std_dev: Optional[float] = None 
    proportion: float = 0.5 


class RiskRow(BaseModel):
    process_step: str = Field(..., description="Paso del proceso")
    failure_mode: str = Field(..., description="Modo de falla (Qué puede salir mal)")
    effect: str = Field(..., description="Efecto (Consecuencia)")
    severity: int = Field(..., ge=1, le=10, description="Severidad (1-10)")
    cause: str = Field(..., description="Causa raíz potencial")
    occurrence: int = Field(..., ge=1, le=10, description="Ocurrencia (1-10)")
    current_controls: str = Field(..., description="Controles actuales")
    detection: int = Field(..., ge=1, le=10, description="Detección (1-10)")

class AnovaParams(BaseModel):
    confidence_level: float = 0.95


class CostCategory(str, Enum):
    PREVENTION = "prevencion"
    APPRAISAL = "evaluacion"
    INTERNAL_FAILURE = "falla_interna"
    EXTERNAL_FAILURE = "falla_externa"

class CostItem(BaseModel):
    description: str = Field(..., description="Descripción del gasto (ej: Retrabajo)")
    amount: float = Field(..., gt=0, description="Monto monetario")
    category: CostCategory = Field(..., description="Categoría del costo")

# El 'data' del request será: List[CostItem]
# El 'parameters' podría incluir ingresos totales para calcular % de impacto
class CostTreeParams(BaseModel):
    total_revenue: Optional[float] = None # Para calcular impacto sobre ventas


# backend/app/schemas.py (Añade esto)

class TreeItem(BaseModel):
    id: str = Field(..., description="Identificador único del nodo (ej: '1', '1.1')")
    label: str = Field(..., description="Texto del nodo (ej: 'Tiempo de espera')")
    parent_id: Optional[str] = Field(None, description="ID del nodo padre (Null si es raíz)")
    type: str = Field("step", description="Tipo de nodo: 'need', 'driver', 'ctq', 'task', 'step'")
    description: Optional[str] = None

# El 'data' del request será: List[TreeItem]

# backend/app/schemas.py (Añade esto)

# No se requiere un Params específico complejo, pero podríamos añadir opciones
class BoxPlotParams(BaseModel):
    orientation: str = "vertical" # Opcional, para saber cómo presentar el texto
    include_outliers: bool = True


# backend/app/schemas.py (Añade esto)

class IdeaItem(BaseModel):
    text: str = Field(..., description="El texto de la idea")
    votes: int = Field(1, ge=1, description="Votos iniciales (por defecto 1)")
    category: Optional[str] = Field("General", description="Categoría (ej: Mano de Obra)")

# El 'data' será: List[IdeaItem]

# backend/app/schemas.py
# (Asegúrate de tener CapabilityParams o usa uno genérico ZBenchParams con la misma estructura)
class ZBenchParams(BaseModel):
    usl: Optional[float] = None  # Límite Superior (puede ser opcional si solo hay uno)
    lsl: Optional[float] = None  # Límite Inferior
    target: Optional[float] = None
    shift: float = 1.5           # Desplazamiento Sigma estándar (Shift)

# backend/app/schemas.py (Añade esto)

class SpcParams(BaseModel):
    chart_type: str = "xbar_r" # Por ahora solo soportamos este, preparado para 'xbar_s', 'p', etc.
    subgroup_size: Optional[int] = None # Si los datos vienen planos, los agrupamos automáticamente

# El 'data' puede ser:
# Opción A (Datos planos): [{"valor": 10}, {"valor": 12}, ...] (El sistema los agrupa de 5 en 5)
# Opción B (Ya agrupados): [{"subgrupo": 1, "valores": [10, 12, 11]}, ...]

# backend/app/schemas.py (Añade esto)
from datetime import date

class GanttTask(BaseModel):
    task_name: str = Field(..., description="Nombre de la tarea o fase")
    start_date: date = Field(..., description="Fecha de inicio (YYYY-MM-DD)")
    end_date: date = Field(..., description="Fecha de fin (YYYY-MM-DD)")
    phase: Optional[str] = Field("General", description="Fase DMAIC a la que pertenece")
    progress: int = Field(0, ge=0, le=100, description="Porcentaje de avance")

# El 'data' será: List[GanttTask]
# backend/app/schemas.py (Añade esto)

class CashFlowItem(BaseModel):
    description: str = Field(..., description="Concepto (ej: Licencia Software)")
    amount: float = Field(..., gt=0, description="Monto monetario")
    type: Literal["cost", "benefit"] = Field(..., description="Tipo de flujo")
    period: int = Field(0, ge=0, description="Periodo (Mes/Año). 0 = Inversión inicial")

# El 'data' será: List[CashFlowItem]
class CostBenefitParams(BaseModel):
    period_unit: str = "Meses" # Etiqueta para el tiempo
    discount_rate: float = 0.0 # Tasa de descuento para VAN (opcional)

    # backend/app/schemas.py (Añade esto)

class AffinityParams(BaseModel):
    num_clusters: int = Field(3, ge=2, description="Número de grupos deseados")
    auto_label: bool = Field(True, description="Intentar nombrar los grupos automáticamente")

# El 'data' será una lista simple de objetos: [{"text": "Idea 1"}, {"text": "Idea 2"}]


# backend/app/schemas.py (Añade esto)

class RadarPoint(BaseModel):
    category: str = Field(..., description="El eje del radar (ej: 'Seguridad', 'Calidad')")
    value: float = Field(..., ge=0, description="El valor numérico")
    series: str = Field("Actual", description="Nombre de la serie (ej: 'Meta', 'Real')")

# El 'data' será: List[RadarPoint]
# El 'parameters' puede incluir 'max_scale' para fijar el límite del gráfico (ej: 5 o 100)
class RadarParams(BaseModel):
    max_scale: Optional[float] = None # Si no se envía, se calcula automático

# backend/app/schemas.py

class DoeParams(BaseModel):
    response_column: Optional[str] = None  # Nombre de la columna "Y" (ej: "Resistencia", "Tiempo")
    # Si no se envía, el sistema asumirá automáticamente que la última columna es la respuesta.


# backend/app/schemas.py

class InterviewItem(BaseModel):
    interviewee: str = Field(..., description="Nombre o Rol del entrevistado (ej: Operador 1)")
    date: str = Field(..., description="Fecha de la entrevista")
    transcript: str = Field(..., description="Texto completo o notas de la entrevista")
    topics: Optional[List[str]] = Field(default=[], description="Temas clave identificados manualmente (opcional)")

class InterviewParams(BaseModel):
    top_n_words: int = Field(10, description="Cantidad de palabras clave a extraer")
    min_word_length: int = Field(4, description="Longitud mínima de palabra para ser considerada relevante")


# backend/app/schemas.py

class IshikawaItem(BaseModel):
    category: str = Field(..., description="Categoría (Mano de Obra, Maquinaria, Materiales, Métodos, Medición, Medio Ambiente)")
    cause: str = Field(..., description="Causa raíz principal")
    sub_causes: Optional[List[str]] = Field(default=[], description="Causas secundarias o porqués")

# El 'data' del request será: List[IshikawaItem]


# backend/app/schemas.py

class StratificationParams(BaseModel):
    factor_column: str = Field(..., description="Columna categórica para agrupar (el estrato, ej: 'Turno')")
    target_column: str = Field(..., description="Columna numérica a analizar (ej: 'Defectos', 'Tiempo')")
    # Opcional: Qué operación priorizar en el gráfico
    metric: str = Field("mean", description="Métrica principal para el gráfico: 'count', 'sum', 'mean'")


    # backend/app/schemas.py (Añade esto)

class FmeaItem(BaseModel):
    function_part: str = Field(..., description="Función o Parte del proceso")
    failure_mode: str = Field(..., description="Modo potencial de falla")
    effect: str = Field(..., description="Efecto potencial de la falla")
    severity: int = Field(..., ge=1, le=10, description="Severidad (S)")
    cause: str = Field(..., description="Causa potencial")
    occurrence: int = Field(..., ge=1, le=10, description="Ocurrencia (O)")
    current_controls: str = Field(..., description="Controles actuales")
    detection: int = Field(..., ge=1, le=10, description="Detección (D)")
    recommended_action: Optional[str] = Field(None, description="Acción recomendada (Opcional)")

# El 'data' será: List[FmeaItem]

# backend/app/schemas.py (Añade esto)

class GageItem(BaseModel):
    operator: str = Field(..., description="Nombre o ID del operador")
    part: str = Field(..., description="ID de la pieza o parte medida")
    measurement: float = Field(..., description="Valor medido")

# El 'data' será: List[GageItem]
class GageParams(BaseModel):
    tolerance: Optional[float] = Field(None, description="Tolerancia del proceso (USL - LSL) para calcular %Tolerancia")
    sigma_multiplier: float = Field(6.0, description="Multiplicador Sigma (usualmente 6 o 5.15)")

# backend/app/schemas.py (Añade esto)

class RunChartParams(BaseModel):
    center_line: Literal["mean", "median"] = "median" # Six Sigma prefiere Mediana para Run Charts

# El 'data' será: [{"time": "08:00", "value": 10}, {"time": "09:00", "value": 12}...]
# backend/app/schemas.py (Añade esto)

class HistogramParams(BaseModel):
    bins: Optional[int] = Field(None, description="Número de barras (bins). Si se omite, es automático.")
    normality_test: bool = Field(True, description="Ejecutar prueba de normalidad")

# backend/app/schemas.py (Añade esto)

class ConfidenceIntervalParams(BaseModel):
    confidence_level: float = Field(0.95, ge=0.0, le=1.0, description="Nivel de confianza (ej: 0.95 para 95%)")
    variable_type: Literal["mean", "proportion"] = Field("mean", description="Tipo de estimación: 'mean' (Media) o 'proportion' (Proporción)")
    target_value: Optional[float] = Field(None, description="Valor objetivo a comparar (ej: Meta del cliente)")

# El 'data' será una lista de valores: [{"valor": 10.5}, {"valor": 10.2}...]
# Para proporción, pueden ser numéricos (0/1) o texto ("Pasa"/"Falla").

# backend/app/schemas.py (Añade esto)

class ProcessStep(BaseModel):
    id: str = Field(..., description="Identificador único del paso (ej: 'step1')")
    label: str = Field(..., description="Texto del paso (ej: 'Verificar datos')")
    type: Literal["start", "task", "decision", "end"] = Field("task", description="Tipo de símbolo")
    next_ids: List[str] = Field(default=[], description="Lista de IDs a los que se conecta este paso")
    role: Optional[str] = Field(None, description="Responsable (útil para diagramas de carril/swimlane)")

# El 'data' será: List[ProcessStep]

# backend/app/schemas.py (Añade esto)

class RaciRow(BaseModel):
    task: str = Field(..., description="La tarea o actividad")
    assignments: Dict[str, str] = Field(..., description="Diccionario Rol->Asignación. Ej: {'Gerente': 'A', 'Analista': 'R'}")

# El 'data' será: List[RaciRow]

# backend/app/schemas.py (Añade esto)

class ControlPlanItem(BaseModel):
    process_step: str = Field(..., description="Paso del proceso o máquina")
    characteristic: str = Field(..., description="Característica a controlar (ej: Temperatura, Tiempo)")
    specification: str = Field(..., description="Especificación / Tolerancia (ej: 100 +/- 5)")
    measurement_method: str = Field(..., description="Cómo se mide (ej: Sensor, Visual)")
    sample_size_freq: str = Field(..., description="Tamaño y frecuencia (ej: 5 cada hora)")
    control_method: str = Field(..., description="Método de control (ej: Gráfica X-R, Poka Yoke)")
    reaction_plan: str = Field(..., description="Qué hacer si falla (ej: Detener línea y calibrar)")
    responsible: str = Field(..., description="Quién ejecuta la acción")

# El 'data' será: List[ControlPlanItem]


# backend/app/schemas.py (Añade esto)

class ParetoItem(BaseModel):
    label: str = Field(..., description="Categoría del defecto o ítem (ej: 'Rotura', 'Retraso')")
    value: float = Field(..., gt=0, description="Valor (Frecuencia, Costo, Tiempo)")

class ParetoParams(BaseModel):
    limit_a: int = Field(80, description="Límite porcentual para Clase A (Vitales)")
    limit_b: int = Field(95, description="Límite porcentual para Clase B (A + B)")
    # El resto será C

# El 'data' será: List[ParetoItem]

# backend/app/schemas.py

class QfdItem(BaseModel):
    customer_req: str = Field(..., description="QUÉ: Requerimiento del cliente (ej: 'Fácil de abrir')")
    weight: int = Field(..., ge=1, le=10, description="Importancia para el cliente (1-5 o 1-10)")
    # Relación: 9 (Fuerte), 3 (Media), 1 (Débil), 0 (Nula)
    relationships: Dict[str, int] = Field(..., description="Relación con los CÓMOs. Clave=NombreTecnico")

class QfdParams(BaseModel):
    technical_reqs: List[str] = Field(..., description="Lista de los CÓMOs (Requerimientos Técnicos)")

# El 'data' será: List[QfdItem]

# backend/app/schemas.py (Añade esto)

class RegressionParams(BaseModel):
    target_column: str = Field(..., description="La variable dependiente (Y) que queremos predecir.")
    # Opcional: Lista de columnas a usar como X. Si se omite, usa todas las numéricas restantes.
    predictors: Optional[List[str]] = Field(None, description="Lista de variables independientes (Xs).")

# backend/app/schemas.py

class RsmParams(BaseModel):
    target_column: str = Field(..., description="Variable de respuesta (Y) a optimizar.")
    factors: List[str] = Field(..., description="Lista de factores (Xs). Idealmente 2 para visualización 3D.")
    goal: Literal["maximize", "minimize"] = Field("maximize", description="Objetivo de la optimización.")

# El 'data' es una lista de resultados experimentales: 
# [{"Temp": 20, "Presion": 100, "Yield": 80}, ...]

# backend/app/schemas.py (Añade esto)

class HypothesisParams(BaseModel):
    test_type: Literal["1_sample", "2_sample", "paired"] = Field(..., description="Tipo de prueba T")
    target_value: Optional[float] = Field(None, description="Valor meta (solo para 1_sample)")
    alpha: float = Field(0.05, description="Nivel de significancia (0.05 = 95% confianza)")
    # Nombres de columnas opcionales (si no se envían, el sistema intenta adivinar)
    group_column: Optional[str] = None 
    value_column: Optional[str] = None
    column_1: Optional[str] = None # Para Paired (ej: 'Antes')
    column_2: Optional[str] = None # Para Paired (ej: 'Despues')

# backend/app/schemas.py

class NormalityTestParams(BaseModel):
    alpha: float = Field(0.05, description="Nivel de significancia (ej: 0.05 para 95% confianza)")
    # Opcional: Elegir método específico si se desea
    method: Literal["auto", "anderson", "shapiro"] = "auto"

# El 'data' es una lista simple de valores: [{"valor": 10}, {"valor": 12}...]

# backend/app/schemas.py

class ChiSquareParams(BaseModel):
    row_column: str = Field(..., description="Nombre de la columna para las filas (ej: 'Turno')")
    col_column: str = Field(..., description="Nombre de la columna para las columnas (ej: 'Defecto')")
    alpha: float = Field(0.05, description="Nivel de significancia")

# El 'data' es la lista cruda: [{"Turno": "A", "Defecto": "Si"}, {"Turno": "A", "Defecto": "No"}...]

# backend/app/schemas.py

class BscItem(BaseModel):
    perspective: Literal["Financiera", "Cliente", "Procesos Internos", "Aprendizaje y Crecimiento"] = Field(..., description="Una de las 4 perspectivas del BSC")
    kpi: str = Field(..., description="Nombre del indicador (ej: ROI, Satisfacción)")
    target: float = Field(..., description="Meta esperada")
    actual: float = Field(..., description="Valor real obtenido")
    # Opcional: 'higher_is_better' (True/False). Por defecto asumimos que MÁS es MEJOR.
    higher_is_better: bool = Field(True, description="True si queremos maximizar, False si queremos minimizar (ej: Defectos)")

# El 'data' será: List[BscItem]

# backend/app/schemas.py

class PmiItem(BaseModel):
    text: str = Field(..., description="La idea o aspecto a evaluar")
    type: Literal["Plus", "Minus", "Interesting"] = Field(..., description="Clasificación: Plus (Positivo), Minus (Negativo), Interesting (Interesante)")
    weight: int = Field(1, ge=1, le=10, description="Peso o impacto del punto (1-10). Por defecto 1.")

# El 'data' será: List[PmiItem]

# ... (todo el código que ya tenías antes) ...

# Agrega esto al final:
class RecommendationRequest(BaseModel):
    phase: str = Field(..., description="Fase DMAIC (Define, Measure, Analyze, Improve, Control)")
    description: str = Field(..., description="Descripción del problema para que la IA recomiende")