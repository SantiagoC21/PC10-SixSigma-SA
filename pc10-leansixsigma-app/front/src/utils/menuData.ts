// src/utils/menuData.ts

export const DMAIC_STRUCTURE = [
  {
    phase: "Definir",
    id: "Define",
    tools: [
      { name: "Arbol de Costos", path: "cost_tree" },
      { name: "Brainstorming", path: "brainstorming" },
      { name: "Grafico de Gantt", path: "gantt" },
      { name: "Costo y Beneficio", path: "cost_benefit" },
      { name: "Diagrama de Afinidades", path: "affinity_diagram" },
      { name: "Mapa de Procesos", path: "process_map" },
      { name: "Mapa de Responsabilidades", path: "responsabilities_map" },
      { name: "QFD", path: "QFD" },
      { name: "PMI", path: "PMI" }
    ]
  },
  {
    phase: "Medir",
    id: "Measure",
    tools: [
      { name: "Muestreo", path: "sampling" }, 
      { name: "Arbol de Costos", path: "cost_tree" },
      { name: "Arbol de Estructura", path: "tree_structure" },
      { name: "Diagrama de Caja", path: "boxplot" },
      { name: "Brainstorming", path: "brainstorming" },
      { name: "Z Bench", path: "z_bench" },
      { name: "Grafico de Gantt", path: "gantt" },
      { name: "Diagrama de Dispersión", path: "scatter_diagram" },
      { name: "Diagrama de Radar", path: "Radar Chart" },
      { name: "Entrevistas", path: "interviews" },
      { name: "Estratificaciones", path: "estratification" },
      { name: "Gage R&R", path: "gage_rr" },
      { name: "Grafico de series temporales", path: "series_graph" },
      { name: "Histograma", path: "histogram" },
      { name: "Intervalo de Confianza", path: "confidence_interval" },
      { name: "Pareto - ABC", path: "abc_pareto" },
      { name: "Prueba de Normalidad", path: "normality" }
    ]
  },
  {
    phase: "Analizar",
    id: "Analyze",
    tools: [
      { name: "ANOVA", path: "anova" },
      { name: "Diagrama de Caja", path: "boxplot" },
      { name: "Brainstorming", path: "brainstorming" },
      { name: "Grafico de Gantt", path: "gantt" },
      { name: "Diagrama de Afinidades", path: "affinity_diagram" },
      { name: "Diagrama de Experimentos", path: "affinity_diagram" },
      { name: "Entrevistas", path: "interviews" },
      { name: "Diagrama Causa-Efecto", path: "ishikawa" },
      { name: "Estratificaciones", path: "estratification" },
      { name: "Análisis de Modo y Efecto de Falla", path: "fmea" },
      { name: "Grafico de series temporales", path: "series_graph" },
      { name: "Histograma", path: "histogram" },
      { name: "Intervalo de Confianza", path: "confidence_interval" },
      { name: "Mapa de Procesos", path: "process_map" },
      { name: "Matriz de Causa Efecto", path: "cause_effect_matrix" },
      { name: "Pareto - ABC", path: "abc_pareto" },
      { name: "Regresión", path: "regression" },
      { name: "Prueba de hipótesis", path: "hypothesis" },
      { name: "Prueba de Chi-quadrado", path: "chi_square" }
    ]
  },
  {
    phase: "Mejorar",
    id: "Improve",
    tools: [
      
      { name: "Muestreo", path: "sampling" },
      { name: "Análisis de Riesgos", path: "risk_analysis" },
      { name: "Z Bench", path: "z_bench" },
      { name: "Grafico de Gantt", path: "gantt" },
      { name: "Costo y Beneficio", path: "cost_benefit" },
      { name: "Diagrama de Experimentos", path: "affinity_diagram" },
      { name: "Análisis de Modo y Efecto de Falla", path: "fmea" },
      { name: "Intervalo de Confianza", path: "confidence_interval" },
      { name: "Pareto - ABC", path: "abc_pareto" },
      { name: "Regresión", path: "regression" },
      { name: "Superficie de Respuesta", path: "rsm" }
    ]
  },
  {
    phase: "Controlar",
    id: "Control",
    tools: [
      { name: "Z Bench", path: "z_bench" },
      { name: "Control Estadístico de Procesos", path: "cep" },
      { name: "Grafico de Gantt", path: "gantt" },
      { name: "Costo y Beneficio", path: "cost_benefit" },
      { name: "Intervalo de Confianza", path: "confidence_interval" },
      { name: "Mapa de Responsabilidades", path: "responsabilities_map" },
      { name: "Plan de Control", path: "control_plan" },
      { name: "Balanced Scorecard", path: "bsc" },
      { name: "PMI", path: "PMI" }
    ]
  }
];