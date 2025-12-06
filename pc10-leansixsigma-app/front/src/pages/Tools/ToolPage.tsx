import { useMemo } from 'react';
import { useParams } from 'react-router-dom';
import styles from './ToolPage.module.css';

type PhaseTag = 'D' | 'M' | 'A' | 'I' | 'C';

type ToolConfig = {
  id: string;
  name: string;
  phases: PhaseTag[];
  summary: string;
  objectives: string[];
  inputs: string[];
  outputs: string[];
  metrics: { label: string; hint: string };
  steps: string[];
  checklist: string[];
  tips: string[];
};

const PHASE_LABEL: Record<PhaseTag, string> = {
  D: 'Definir',
  M: 'Medir',
  A: 'Analizar',
  I: 'Innovar',
  C: 'Controlar',
};

const TOOL_REGISTRY: Record<string, ToolConfig> = {
  stratification: {
    id: 'stratification',
    name: 'Estratificaciones',
    phases: ['M', 'A'],
    summary: 'Segmenta datos por categorías clave (turno, línea, cliente) para descubrir patrones ocultos y reducir la variabilidad.',
    objectives: [
      'Identificar subgrupos que explican la mayor variación del proceso.',
      'Priorizar causas potenciales según la magnitud de diferencia entre estratos.',
    ],
    inputs: [
      'Datos crudos con variable de resultado (Y) y categorizaciones (turno, línea, cliente, producto).',
      'Volumen por categoría para verificar representatividad.',
    ],
    outputs: [
      'Tabla de comparación entre estratos (medias, medianas, % defectos).',
      'Visualizaciones rápidas (boxplot / barras) para discutir con el equipo.',
    ],
    metrics: { label: 'Variación entre estratos', hint: 'Diferencia de medias o % de defectos por categoría' },
    steps: [
      'Listar las variables de estratificación relevantes (personas, máquina, materia prima, turno, clima).',
      'Construir tabla comparativa y marcar el estrato con peor desempeño.',
      'Validar tamaño de muestra por estrato; si es bajo, planificar recolección.',
      'Decidir siguientes análisis: Pareto dentro del estrato crítico o hipótesis estadística.',
    ],
    checklist: [
      '¿Las categorías son excluyentes y completas?',
      '¿Existe al menos 80% de cobertura de datos por estrato?',
      '¿Hay diferencias significativas o solo ruido?',
    ],
    tips: [
      'Combina con Pareto para ordenar causas dentro del estrato crítico.',
      'Si hay muchos estratos, agrupa por riesgo/impacto para enfocar la discusión.',
    ],
  },
  muestreo: {
    id: 'muestreo',
    name: 'Muestreo',
    phases: ['M', 'I'],
    summary: 'Define cuántas observaciones tomar, con qué frecuencia y método, para que los datos sean confiables sin sobredimensionar el esfuerzo.',
    objectives: [
      'Elegir tipo de muestreo (aleatorio, sistemático, estratificado) acorde a la variabilidad del proceso.',
      'Dimensionar el tamaño de muestra para lograr la precisión requerida.',
    ],
    inputs: [
      'Población estimada o tasa de ocurrencia.',
      'Variabilidad histórica (desvío estándar o % defectos) y nivel de confianza deseado.',
    ],
    outputs: [
      'Plan de muestreo con tamaño, frecuencia, responsables y punto de captura.',
      'Instrucciones de medición y formato de registro.',
    ],
    metrics: { label: 'Error objetivo', hint: '± precisión esperada en % o unidades' },
    steps: [
      'Definir el objetivo de medición (nivel de defecto, tiempo, capacidad).',
      'Seleccionar técnica de muestreo según estabilidad y accesibilidad del proceso.',
      'Calcular tamaño de muestra; ajustar por costo/tiempo y riesgo.',
      'Documentar roles, frecuencia y controles de calidad de datos.',
    ],
    checklist: [
      '¿El punto de toma de datos es consistente y repetible?',
      '¿Los operadores conocen el formato y las variables a registrar?',
      '¿Se evita sesgo de selección (solo turnos buenos/malos)?',
    ],
    tips: [
      'Si el proceso cambia por turno, usa muestreo estratificado por turno.',
      'Revisa Gage R&R antes de escalar la recolección masiva.',
    ],
  },
  risk_analysis: {
    id: 'risk_analysis',
    name: 'Análisis de riesgos',
    phases: ['I'],
    summary: 'Evalúa riesgos de las soluciones propuestas considerando probabilidad, impacto y detección para priorizar mitigaciones.',
    objectives: [
      'Comparar alternativas de mejora con un lenguaje común de riesgo.',
      'Definir acciones preventivas antes de implementar.',
    ],
    inputs: [
      'Lista de soluciones candidatas y supuestos clave.',
      'Riesgos identificados: técnicos, de proceso, de cliente y de cumplimiento.',
    ],
    outputs: [
      'Matriz de riesgos con RPN o nivel de exposición.',
      'Plan de respuesta (mitigar, transferir, aceptar) y dueños.',
    ],
    metrics: { label: 'RPN / Exposición', hint: 'Probabilidad x Impacto x Detección o escala definida' },
    steps: [
      'Enumerar riesgos por solución y agruparlos por categoría.',
      'Asignar probabilidad, impacto y detectabilidad en escala común.',
      'Ordenar por RPN y proponer mitigaciones mínimas viables.',
      'Aprobar acciones antes del piloto y monitorear residual.',
    ],
    checklist: [
      '¿Incluiste riesgos de cambio organizacional y de datos?',
      '¿Los criterios de impacto están alineados con objetivos del proyecto?',
      '¿Cada mitigación tiene responsable y fecha?',
    ],
    tips: [
      'Usa aprendizajes de FMEA para completar riesgos técnicos.',
      'Vincula cada riesgo a un KPI de control para seguimiento post-implementación.',
    ],
  },
  chi_square: {
    id: 'chi_square',
    name: 'Prueba de Chi-quadrado',
    phases: ['A'],
    summary: 'Contrasta si dos variables categóricas están asociadas (ej. turno vs. defecto) sin asumir distribución normal.',
    objectives: [
      'Validar si la diferencia observada entre categorías es estadísticamente significativa.',
      'Respaldar decisiones de priorización con evidencia.',
    ],
    inputs: [
      'Tabla de contingencia con frecuencias observadas.',
      'Tamaño de muestra suficiente por celda (ideal >5).',
    ],
    outputs: [
      'Valor p y conclusión sobre dependencia/independencia.',
      'Celdas que más contribuyen al estadístico (residuos).',
    ],
    metrics: { label: 'Valor p', hint: 'Comparado con alfa (ej. 0.05)' },
    steps: [
      'Formular hipótesis H0: no hay asociación; H1: existe asociación.',
      'Calcular frecuencias esperadas y estadístico Chi-cuadrado.',
      'Revisar valor p y residuos para interpretar contribución de cada celda.',
      'Documentar conclusión y decisión práctica.',
    ],
    checklist: [
      '¿Las frecuencias esperadas cumplen criterio mínimo?',
      '¿La muestra representa el periodo de interés?',
      '¿Se documenta alfa y efecto práctico, no solo significancia?',
    ],
    tips: [
      'Si hay celdas bajas, combina categorías o usa prueba exacta de Fisher.',
      'Complementa con Pareto dentro de la categoría crítica identificada.',
    ],
  },
  doe: {
    id: 'doe',
    name: 'Diseño de experimentos (DOE)',
    phases: ['A', 'I'],
    summary: 'Planifica experimentos controlados para entender efectos principales e interacciones con el mínimo número de corridas.',
    objectives: [
      'Identificar factores críticos (X) y su impacto en la respuesta (Y).',
      'Optimizar parámetros reduciendo la variabilidad.',
    ],
    inputs: [
      'Lista de factores controlables y niveles propuestos.',
      'Restricciones operativas (tiempo de set-up, costos, seguridad).',
    ],
    outputs: [
      'Matriz de diseño (ej. 2^k fraccionado o factorial completo).',
      'Efectos estimados, gráficas de interacción y recomendación de ajuste.',
    ],
    metrics: { label: 'Señal/ruido esperado', hint: 'Relación entre efecto mínimo detectable y ruido del proceso' },
    steps: [
      'Definir respuesta Y y rango operativo seguro.',
      'Seleccionar diseño (factorial, fraccionado, central compuesto) según recursos.',
      'Ejecutar corridas aleatorizadas y registrar condiciones.',
      'Analizar efectos, validar supuestos y recomendar seteo óptimo.',
    ],
    checklist: [
      '¿Los factores son controlables y medibles?',
      '¿Se aleatorizó el orden para evitar sesgos de tiempo?',
      '¿Se verifican supuestos de normalidad y homocedasticidad en residuos?',
    ],
    tips: [
      'Empieza con fraccionado para explorar; profundiza con diseño de respuesta si hay curvatura.',
      'Bloquea por turno/línea si no puedes aleatorizar completamente.',
    ],
  },
  regression: {
    id: 'regression',
    name: 'Regresión',
    phases: ['A', 'I'],
    summary: 'Modela la relación entre variables X y Y para cuantificar impacto, predecir resultados y soportar decisiones de ajuste.',
    objectives: [
      'Identificar variables significativas y magnitud de su efecto.',
      'Predecir desempeño bajo distintos escenarios.',
    ],
    inputs: [
      'Dataset con Y numérica y posibles X (continuas / categóricas codificadas).',
      'Variables centradas/escalares para evitar colinealidad.',
    ],
    outputs: [
      'Coeficientes, R² ajustado y error de predicción.',
      'Gráficos de residuos y diagnóstico de supuestos.',
    ],
    metrics: { label: 'R² ajustado', hint: 'Calidad del ajuste corrigiendo por número de predictores' },
    steps: [
      'Explorar correlaciones y colinealidad (VIF).',
      'Ajustar modelo inicial y simplificar con criterios de información.',
      'Validar supuestos (linealidad, homocedasticidad, normalidad de residuos).',
      'Calibrar el modelo final y traducir en reglas operativas.',
    ],
    checklist: [
      '¿Variables categóricas correctamente codificadas?',
      '¿Se evita extrapolar fuera del rango observado?',
      '¿Se reporta intervalo de confianza de las predicciones?',
    ],
    tips: [
      'Usa transforms log/sqrt si la relación es curvilínea.',
      'Para priorizar acciones, convierte coeficientes a impacto práctico (unidades de negocio).',
    ],
  },
  spc: {
    id: 'spc',
    name: 'CEP (control estadístico Procesos)',
    phases: ['C'],
    summary: 'Monitorea estabilidad del proceso con gráficas de control y reglas de detección temprana.',
    objectives: [
      'Diferenciar variación común de variación especial.',
      'Definir reacción estándar ante señales de fuera de control.',
    ],
    inputs: [
      'Datos cronológicos con timestamp y variable Y.',
      'Tamaño de subgrupo si aplica (n para Xbar-R/Xbar-S).',
    ],
    outputs: [
      'Límites de control calculados y gráficos SPC listos para operar.',
      'Guía de respuesta por tipo de señal (punto fuera, tendencia, run).',
    ],
    metrics: { label: 'Estado del proceso', hint: 'Estable / fuera de control + número de señales' },
    steps: [
      'Verificar estabilidad inicial (eliminar causas especiales conocidas).',
      'Elegir tipo de carta (I-MR, Xbar-R, p, u) según datos.',
      'Calcular límites de control y marcar señales de Western Electric.',
      'Acordar plan de reacción y responsables.',
    ],
    checklist: [
      '¿Las reglas de señal están alineadas con criticidad del proceso?',
      '¿Se almacenan causas asignables para aprendizaje futuro?',
      '¿Operaciones conoce qué detener y qué escalar?',
    ],
    tips: [
      'Complementa con Run Chart si no hay suficientes datos para límites robustos.',
      'Recalcula límites solo después de mejoras significativas y estables.',
    ],
  },
  pareto: {
    id: 'pareto',
    name: 'Pareto / ABC',
    phases: ['M', 'A', 'I'],
    summary: 'Ordena causas o categorías por contribución acumulada para enfocar esfuerzo donde está la mayor pérdida.',
    objectives: [
      'Identificar el 20% de causas que explican ~80% del impacto.',
      'Sustentar la priorización con datos y frecuencia.',
    ],
    inputs: [
      'Conteos o costo por categoría de defecto / causa.',
      'Periodo de análisis representativo.',
    ],
    outputs: [
      'Tabla ordenada con porcentaje y acumulado.',
      'Gráfico Pareto y categoría de corte.',
    ],
    metrics: { label: 'Cobertura top', hint: '% de impacto cubierto por las primeras categorías' },
    steps: [
      'Definir unidad de impacto (conteo, tiempo perdido, costo).',
      'Ordenar de mayor a menor y calcular % acumulado.',
      'Marcar punto de corte (ej. 70-80%) y validar con equipo.',
      'Planear acciones sobre la categoría crítica.',
    ],
    checklist: [
      '¿Las categorías son mutuamente excluyentes?',
      '¿Periodo incluye variabilidad estacional?',
      '¿La métrica de impacto está alineada a CTQ/CTC?',
    ],
    tips: [
      'Si hay muchas categorías pequeñas, agrupa en “otros” y re-analiza.',
      'Repite después de mejoras para verificar desplazamiento de la curva.',
    ],
  },
  hypothesis: {
    id: 'hypothesis',
    name: 'Prueba de hipótesis',
    phases: ['A'],
    summary: 'Evalúa diferencias entre grupos o contra un objetivo usando pruebas t, z o no paramétricas, según el tipo de dato.',
    objectives: [
      'Confirmar si la diferencia observada es estadísticamente significativa.',
      'Respaldar decisiones de cambio con evidencia cuantitativa.',
    ],
    inputs: [
      'Muestras con Y numérica o proporción y definición de alfa.',
      'Supuestos de normalidad/varianzas o selección de prueba robusta.',
    ],
    outputs: [
      'Valor p, intervalo de confianza y decisión H0/H1.',
      'Magnitud de efecto (práctico) para priorizar.',
    ],
    metrics: { label: 'Valor p y efecto', hint: 'p-value + d de Cohen o diferencia absoluta' },
    steps: [
      'Plantear hipótesis y nivel de significancia.',
      'Elegir prueba según tipo de dato y varianzas (t, z, Mann-Whitney, etc.).',
      'Ejecutar prueba, revisar supuestos y calcular efecto.',
      'Documentar decisión y acción recomendada.',
    ],
    checklist: [
      '¿Se cumplen supuestos o se usó versión no paramétrica?',
      '¿La muestra cubre la variabilidad real del proceso?',
      '¿Se interpretó el efecto práctico, no solo el estadístico?',
    ],
    tips: [
      'Usa gráficos (boxplot, densidades) para soporte visual.',
      'Si hay múltiples comparaciones, controla error (Bonferroni/FDR).',
    ],
  },
  gage_rr: {
    id: 'gage_rr',
    name: 'Gage R&R',
    phases: ['M'],
    summary: 'Cuantifica variación del sistema de medición (repetibilidad y reproducibilidad) para asegurar datos confiables.',
    objectives: [
      'Verificar que el error de medición sea pequeño frente a la variación del proceso.',
      'Detectar sesgos por operador o instrumento.',
    ],
    inputs: [
      'Piezas representativas del rango operativo.',
      'Múltiples operadores y repeticiones por pieza.',
    ],
    outputs: [
      '%GRR sobre variación total y por componente.',
      'Conclusión: aceptar, mejorar método o cambiar instrumento.',
    ],
    metrics: { label: '%GRR', hint: '% de variación atribuible al sistema de medición' },
    steps: [
      'Seleccionar piezas cubriendo el rango completo.',
      'Definir operadores y repeticiones; aleatorizar el orden de medición.',
      'Ejecutar mediciones y analizar componentes (ANOVA o rango).',
      'Plan de mejora si %GRR > 10-30% según criticidad.',
    ],
    checklist: [
      '¿Piezas limpias y sin marcas visibles de mediciones previas?',
      '¿Operadores entrenados con el mismo método?',
      '¿Instrumento calibrado y en ambiente estable?',
    ],
    tips: [
      'Si hay variación por operador, estandariza técnica y sujeción.',
      'Para variables discretas, usa atributo agreement (Kappa, % acuerdo).',
    ],
  },
  fmea: {
    id: 'fmea',
    name: 'Análisis de Modo y Efecto de Falla (FMEA)',
    phases: ['A', 'I'],
    summary: 'Identifica modos de falla, sus efectos y prioriza acciones según severidad, ocurrencia y detección.',
    objectives: [
      'Prevenir fallas críticas antes de implementar soluciones.',
      'Alinear responsables y fechas de cierre para riesgos altos.',
    ],
    inputs: [
      'Mapa de proceso y lista de pasos clave.',
      'Historial de fallas, reclamos y scrap.',
    ],
    outputs: [
      'Tabla FMEA con RPN/acción priorizada.',
      'Plan de mitigación con responsables y fecha.',
    ],
    metrics: { label: 'RPN / Acción crítica', hint: 'Top modos de falla y estatus de acción' },
    steps: [
      'Listar pasos del proceso y posibles modos de falla.',
      'Asignar severidad, ocurrencia y detección con escala acordada.',
      'Ordenar por RPN o matriz de criticidad y definir acciones.',
      'Re-evaluar RPN residual y actualizar plan.',
    ],
    checklist: [
      '¿Participan operaciones, calidad y mantenimiento?',
      '¿Escalas de S/O/D están alineadas con políticas internas?',
      '¿Acciones tienen dueños y fechas?',
    ],
    tips: [
      'Conecta acciones de alta prioridad con SPC o Poka-Yoke para control sostenido.',
      'Revisar FMEA después de cada cambio de proceso.',
    ],
  },
  radar: {
    id: 'radar',
    name: 'Diagrama de Radar / Radar Chart',
    phases: ['M'],
    summary: 'Visualiza múltiples CTQs en una sola gráfica para comparar rendimiento entre líneas, proveedores o periodos.',
    objectives: [
      'Comparar desempeño relativo en varias dimensiones.',
      'Detectar desequilibrios o cuellos de botella visibles.',
    ],
    inputs: [
      'Métricas normalizadas (0-1) o escaladas uniformemente.',
      'Etiquetas de ejes y series a comparar.',
    ],
    outputs: [
      'Gráfico radar con áreas destacadas.',
      'Lista de dimensiones bajo el umbral objetivo.',
    ],
    metrics: { label: 'Gap vs objetivo', hint: 'Dimensiones por debajo del nivel esperado' },
    steps: [
      'Seleccionar CTQs y normalizarlos a escala común.',
      'Armar el gráfico para series clave (línea, proveedor, periodo).',
      'Resaltar dimensiones críticas y priorizar acción.',
      'Comunicar hallazgos con responsable por CTQ.',
    ],
    checklist: [
      '¿Mismas unidades o métricas normalizadas?',
      '¿No más de 6-8 dimensiones para claridad?',
      '¿Se identificó dueño por dimensión crítica?',
    ],
    tips: [
      'Combina con Pareto para profundizar en la dimensión más débil.',
      'Usa colores contrastantes y anotaciones breves para la reunión.',
    ],
  },
  run_chart: {
    id: 'run_chart',
    name: 'Gráfico de series de tiempo - Run Chart',
    phases: ['M', 'A'],
    summary: 'Muestra tendencia y estacionalidad sin asumir normalidad; útil para detección temprana de cambios.',
    objectives: [
      'Detectar shifts, tendencias o ciclos en el proceso.',
      'Preparar base para SPC cuando aún no hay suficientes datos.',
    ],
    inputs: [
      'Datos secuenciales con timestamp y valor de Y.',
      'Meta o línea de referencia opcional.',
    ],
    outputs: [
      'Gráfico temporal con medias móviles o mediana.',
      'Señales básicas (runs, tendencias).',
    ],
    metrics: { label: 'Señales detectadas', hint: 'Cambios de mediana, runs largos, tendencias' },
    steps: [
      'Graficar datos cronológicos y marcar meta/mediana.',
      'Aplicar reglas de runs (n sobre/under mediana, secuencias).',
      'Documentar posibles causas asignables para cada señal.',
      'Planear siguiente paso: SPC o experimento si hay inestabilidad.',
    ],
    checklist: [
      '¿Fechas/hora correctas y sin huecos grandes?',
      '¿Se separaron periodos con cambios de turno o campaña?',
      '¿Se anotan eventos de proceso en la línea de tiempo?',
    ],
    tips: [
      'Si hay estacionalidad, grafica por facetas (por día de semana/turno).',
      'Complementa con anotaciones de mantenimiento o cambio de insumo.',
    ],
  },
  qfd: {
    id: 'qfd',
    name: 'La casa de calidad (QFD)',
    phases: ['D'],
    summary: 'Traduce la voz del cliente en CTQs y en requisitos técnicos priorizados.',
    objectives: [
      'Conectar necesidades del cliente con especificaciones medibles.',
      'Ordenar características técnicas por impacto en satisfacción.',
    ],
    inputs: [
      'VOC priorizada, CTQs y benchmarks de competidores si existen.',
      'Matriz de correlación entre necesidades y características técnicas.',
    ],
    outputs: [
      'Matriz QFD con pesos relativos y trade-offs visualizados.',
      'Top características técnicas para el diseño o ajuste del proceso.',
    ],
    metrics: { label: 'Peso relativo', hint: 'Importancia acumulada de cada característica técnica' },
    steps: [
      'Recolectar VOC y traducir a CTQs priorizadas.',
      'Listar características técnicas que impactan cada CTQ.',
      'Asignar relación (fuerte/media/débil) y calcular peso.',
      'Discutir trade-offs y seleccionar focos de diseño.',
    ],
    checklist: [
      '¿VOC viene de fuente reciente y representativa?',
      '¿Participan producto, operaciones y calidad en la matriz?',
      '¿Se documentan supuestos de relación y se validan con datos?',
    ],
    tips: [
      'Mantén la matriz acotada; 10-15 CTQs máximas para discusión efectiva.',
      'Usa resultados para alimentar DOE o ajustes de parámetros clave.',
    ],
  },
  bsc: {
    id: 'bsc',
    name: 'Balanced Scorecard',
    phases: ['C'],
    summary: 'Conecta indicadores de proceso con objetivos estratégicos en cuatro perspectivas para un control integral.',
    objectives: [
      'Asegurar alineación entre métricas operativas y resultados estratégicos.',
      'Visibilizar brechas y responsables por KPI.',
    ],
    inputs: [
      'Objetivos estratégicos y metas por perspectiva.',
      'Indicadores actuales con frecuencia y fuente de datos.',
    ],
    outputs: [
      'Mapa de objetivos y KPIs asociados.',
      'Tablero con estatus (verde/amarillo/rojo) y planes de acción.',
    ],
    metrics: { label: 'KPI críticos', hint: 'Listado con meta, tendencia y dueño' },
    steps: [
      'Definir objetivos por perspectiva (financiera, cliente, procesos, aprendizaje).',
      'Seleccionar KPIs accionables y frecuencia de revisión.',
      'Armar tablero y cadencia de follow-up.',
      'Vincular alertas con plan de acción y responsables.',
    ],
    checklist: [
      '¿Cada KPI tiene meta, frecuencia y fuente clara?',
      '¿Se evita exceso de métricas? (máx 3-5 por perspectiva)',
      '¿Los responsables conocen su plan de reacción?',
    ],
    tips: [
      'Integra KPIs de SPC y capacidad para la perspectiva de procesos.',
      'Usa notas de riesgo para anticipar desvíos de largo plazo.',
    ],
  },
  scatter: {
    id: 'scatter',
    name: 'Diagrama de dispersión / Scatter Diagram',
    phases: ['M'],
    summary: 'Explora relación entre dos variables cuantitativas para detectar correlaciones y patrones no lineales.',
    objectives: [
      'Visualizar tendencia, outliers y forma de la relación.',
      'Preparar insumos para modelos o decisiones de ajuste.',
    ],
    inputs: [
      'Parejas (X, Y) con suficiente rango y sin censura.',
      'Opcional: agrupación por categoría para color/forma.',
    ],
    outputs: [
      'Gráfico de dispersión con línea de tendencia opcional.',
      'Lista de outliers y segmentos con comportamiento distinto.',
    ],
    metrics: { label: 'Correlación', hint: 'Coeficiente r o rho según normalidad' },
    steps: [
      'Graficar puntos y revisar forma (lineal, curva, clusters).',
      'Calcular correlación y verificar supuestos.',
      'Marcar outliers y decidir si investigar o excluir con causa.',
      'Concluir si procede modelo (regresión) o prueba de hipótesis.',
    ],
    checklist: [
      '¿Se cubre todo el rango operativo de X?',
      '¿Outliers tienen explicación documentada?',
      '¿Se evita confundir correlación con causalidad?',
    ],
    tips: [
      'Si hay curvatura, prueba transformaciones o modelos no lineales.',
      'Colorea por turno/proveedor para descubrir estratos ocultos.',
    ],
  },
  capability: {
    id: 'capability',
    name: 'Capacidades / Z bench',
    phases: ['M', 'I', 'C'],
    summary: 'Mide qué tan bien el proceso cumple especificaciones (Cp, Cpk, Zbench) y prioriza mejoras en centrado y variabilidad.',
    objectives: [
      'Cuantificar capacidad actual frente a límites de especificación.',
      'Definir necesidad de reducir variación o recentrar el proceso.',
    ],
    inputs: [
      'Datos continuos en estado estable y límites de especificación (LSL/USL).',
      'Validación de medición (Gage) y estabilidad básica.',
    ],
    outputs: [
      'Cp/Cpk o Zbench, histograma con specs y resumen de incumplimientos.',
      'Recomendación: ajustar centrado, reducir variación o ambos.',
    ],
    metrics: { label: 'Cpk / Zbench', hint: 'Nivel de capacidad y probabilidad de defecto' },
    steps: [
      'Verificar estabilidad (Run/SPC) y calidad de medición (Gage).',
      'Calcular capacidad y visualizar con histograma + specs.',
      'Interpretar: ¿el problema es centrado o dispersión?',
      'Planificar acción (DOE, ajustes, mantenimiento) y recalcular post-mejora.',
    ],
    checklist: [
      '¿Proceso estable al momento del cálculo?',
      '¿Datos representan el rango completo de operación?',
      '¿Se comunica la traducción a PPM/defectos por unidad?',
    ],
    tips: [
      'Si no hay normalidad, usa Ppk/no paramétricos o transformar datos.',
      'Mantén histórico para evidenciar mejora sostenida en Control.',
    ],
  },
  anova: {
    id: 'anova',
    name: 'Analisis de varianza (ANOVA)',
    phases: ['A'],
    summary: 'Compara medias de varios grupos para detectar diferencias significativas en el desempeño.',
    objectives: [
      'Determinar si al menos un grupo difiere en su media.',
      'Cuantificar tamaño de efecto y priorizar ajustes.',
    ],
    inputs: [
      'Datos numéricos por grupo con supuestos de normalidad/homocedasticidad o versión robusta.',
      'Número de replicaciones por grupo.',
    ],
    outputs: [
      'F-stat, valor p y comparaciones post-hoc si aplica.',
      'Interpretación práctica (diferencias relevantes).',
    ],
    metrics: { label: 'Valor p / Eta²', hint: 'Significancia y tamaño de efecto' },
    steps: [
      'Verificar supuestos o elegir ANOVA robusto/Kruskal-Wallis.',
      'Ejecutar ANOVA y revisar residuos.',
      'Si es significativo, correr comparaciones múltiples con control de error.',
      'Traducir hallazgos en cambios operativos.',
    ],
    checklist: [
      '¿Grupos balanceados o se ajustó por desbalance?',
      '¿Se reporta tamaño de efecto además de p?',
      '¿Se documentan supuestos y transformaciones usadas?',
    ],
    tips: [
      'Visualiza con boxplots para facilitar discusión.',
      'Si hay interacción esperada, considera DOE en lugar de múltiples ANOVAs.',
    ],
  },
};

const EmptyState = ({ toolId }: { toolId?: string }) => (
  <div className={styles.wrapper}>
    <div className={styles.card}>
      <h2>Herramienta en construcción</h2>
      <p style={{ color: '#475569' }}>
        No hay diseño configurado para <strong>{toolId ?? 'esta ruta'}</strong>. Verifica el identificador o
        usa alguna de las herramientas disponibles en el menú.
      </p>
    </div>
  </div>
);

export const ToolPage = () => {
  const { toolId } = useParams();

  const tool = useMemo(() => {
    if (!toolId) return undefined;
    return TOOL_REGISTRY[toolId];
  }, [toolId]);

  if (!tool) {
    return <EmptyState toolId={toolId} />;
  }

  return (
    <div className={styles.wrapper}>
      <header className={styles.hero}>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>{tool.name}</h1>
          <div className={styles.phaseBadges}>
            {tool.phases.map((p) => (
              <span key={p} className={styles.badge}>
                {PHASE_LABEL[p]}
              </span>
            ))}
          </div>
        </div>
        <p className={styles.summary}>{tool.summary}</p>
      </header>

      <div className={styles.grid}>
        <div className="left">
          <div className={styles.card}>
            <h3>Objetivo clave</h3>
            <ul className={styles.list}>
              {tool.objectives.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>

          <div className={styles.card}>
            <h3>Cómo usarla (pasos sugeridos)</h3>
            <div className={styles.stepList}>
              {tool.steps.map((step, idx) => (
                <div key={step} className={styles.stepItem}>
                  <div className={styles.status}>Paso {idx + 1}</div>
                  <div>{step}</div>
                </div>
              ))}
            </div>
          </div>

          <div className={styles.card}>
            <h3>Checklist rápido</h3>
            <ul className={styles.list}>
              {tool.checklist.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            <div className={styles.tip}>Tip: valida el checklist antes de invertir tiempo en análisis detallado.</div>
          </div>
        </div>

        <div className="right">
          <div className={styles.card}>
            <h3>Entradas mínimas</h3>
            <ul className={styles.list}>
              {tool.inputs.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>

          <div className={styles.card}>
            <h3>Salidas esperadas</h3>
            <ul className={styles.list}>
              {tool.outputs.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>

          <div className={styles.card}>
            <h3>Métrica clave</h3>
            <div className={styles.metricRow}>
              <span>{tool.metrics.label}</span>
              <span className={styles.pill}>{tool.metrics.hint}</span>
            </div>
          </div>

          <div className={styles.card}>
            <h3>Consejos Six Sigma</h3>
            <ul className={styles.list}>
              {tool.tips.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
