
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