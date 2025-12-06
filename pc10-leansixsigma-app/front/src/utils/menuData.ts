// src/utils/menuData.ts

export const DMAIC_STRUCTURE = [
  {
    phase: "Definir",
    id: "Define",
    tools: [
      { name: "Project Charter", path: "project_charter" },
      { name: "SIPOC", path: "sipoc" },
      { name: "Voz del Cliente", path: "voice_of_customer" },
      { name: "La casa de calidad (QFD)", path: "qfd" }
    ]
  },
  {
    phase: "Medir",
    id: "Measure",
    tools: [
      { name: "Estratificaciones", path: "stratification" },
      { name: "Muestreo", path: "muestreo" },
      { name: "Pareto / ABC", path: "pareto" },
      { name: "Gage R&R", path: "gage_rr" },
      { name: "Diagrama de Radar", path: "radar" },
      { name: "Gráfico de series de tiempo (Run Chart)", path: "run_chart" },
      { name: "Diagrama de dispersión", path: "scatter" },
      { name: "Capacidades / Z bench", path: "capability" }
    ]
  },
  {
    phase: "Analizar",
    id: "Analyze",
    tools: [
      { name: "Estratificaciones", path: "stratification" },
      { name: "Pareto / ABC", path: "pareto" },
      { name: "Prueba de Chi-quadrado", path: "chi_square" },
      { name: "Diseño de experimentos (DOE)", path: "doe" },
      { name: "Regresión", path: "regression" },
      { name: "Prueba de hipótesis", path: "hypothesis" },
      { name: "Gráfico de series de tiempo (Run Chart)", path: "run_chart" },
      { name: "Análisis de Modo y Efecto de Falla (FMEA)", path: "fmea" },
      { name: "Análisis de varianza (ANOVA)", path: "anova" }
    ]
  },
  {
    phase: "Mejorar",
    id: "Improve",
    tools: [
      { name: "Muestreo", path: "muestreo" },
      { name: "Análisis de riesgos", path: "risk_analysis" },
      { name: "Diseño de experimentos (DOE)", path: "doe" },
      { name: "Regresión", path: "regression" },
      { name: "Pareto / ABC", path: "pareto" },
      { name: "Análisis de Modo y Efecto de Falla (FMEA)", path: "fmea" },
      { name: "Capacidades / Z bench", path: "capability" }
    ]
  },
  {
    phase: "Controlar",
    id: "Control",
    tools: [
      { name: "CEP (control estadístico de procesos)", path: "spc" },
      { name: "Balanced Scorecard", path: "bsc" },
      { name: "Capacidades / Z bench", path: "capability" }
    ]
  }
];
