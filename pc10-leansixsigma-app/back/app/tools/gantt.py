# backend/app/tools/gantt.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class GanttTool(SixSigmaTool):
    """
    Herramienta de Cronograma / Gráfico de Gantt.
    Organiza tareas, calcula duraciones y valida la planificación del proyecto.
    Referencias:
    - Tesis UAP, pág 59 (Planificación Preliminar del Project Charter).
    - Libro Yellow Belt, pág 22 (Herramientas de Definición - Gantt).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación
        if self.df.empty:
            raise ValueError("Se requiere una lista de tareas con fechas.")

        required_cols = ["task_name", "start_date", "end_date"]
        self.validate_columns(required_cols)

        # 2. Procesamiento de Fechas
        # Convertir a datetime para poder restar y comparar
        self.df['start_date'] = pd.to_datetime(self.df['start_date'])
        self.df['end_date'] = pd.to_datetime(self.df['end_date'])

        # Validar consistencia (Fin no puede ser antes de Inicio)
        invalid_dates = self.df[self.df['end_date'] < self.df['start_date']]
        if not invalid_dates.empty:
            bad_task = invalid_dates.iloc[0]['task_name']
            raise ValueError(f"La tarea '{bad_task}' tiene una fecha de fin anterior a la de inicio.")

        # 3. Cálculos de Duración
        self.df['duration_days'] = (self.df['end_date'] - self.df['start_date']).dt.days
        
        # Asegurar que duración mínima sea 1 día (para visualización)
        self.df['duration_days'] = self.df['duration_days'].apply(lambda x: max(x, 1))

        # 4. Estadísticas del Proyecto
        project_start = self.df['start_date'].min()
        project_end = self.df['end_date'].max()
        total_duration = (project_end - project_start).days
        total_tasks = len(self.df)

        # Calcular avance ponderado (opcional, simple promedio por ahora)
        avg_progress = self.df['progress'].mean() if 'progress' in self.df.columns else 0

        # 5. Ordenamiento Cronológico
        self.df = self.df.sort_values(by='start_date')

        summary = (
            f"Cronograma del Proyecto: {total_tasks} tareas planificadas. "
            f"Duración total estimada: {total_duration} días "
            f"(del {project_start.strftime('%Y-%m-%d')} al {project_end.strftime('%Y-%m-%d')}). "
            f"Progreso promedio: {avg_progress:.1f}%."
        )

        # 6. Preparar salida para Frontend
        # Formateamos fechas a string ISO para que JS las lea fácil
        chart_data = []
        for _, row in self.df.iterrows():
            chart_data.append({
                "id": row.get("task_name"), # Usamos nombre como ID simple
                "name": row["task_name"],
                "start": row["start_date"].strftime('%Y-%m-%d'),
                "end": row["end_date"].strftime('%Y-%m-%d'),
                "duration": int(row["duration_days"]),
                "phase": row.get("phase", "General"),
                "progress": row.get("progress", 0)
            })

        return AnalysisResult(
            tool_name="Cronograma (Gráfico de Gantt)",
            summary=summary,
            chart_data=chart_data,
            details={
                "project_start": project_start.strftime('%Y-%m-%d'),
                "project_end": project_end.strftime('%Y-%m-%d'),
                "total_days": int(total_duration),
                "phases_detected": self.df['phase'].unique().tolist() if 'phase' in self.df.columns else []
            }
        )