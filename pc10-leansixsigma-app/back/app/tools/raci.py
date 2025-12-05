# backend/app/tools/raci.py
import pandas as pd
from app.tools.base_tool import SixSigmaTool
from app.schemas import AnalysisResult

class RaciTool(SixSigmaTool):
    """
    Herramienta Matriz de Responsabilidades (RACI).
    Valida la asignación de roles y detecta vacíos de responsabilidad.
    Referencias:
    - Tesis UAP, pág 161 (Tabla 50: Actividad de Implementación RACI).
    """

    def analyze(self) -> AnalysisResult:
        # 1. Validación de Entrada
        if self.df.empty:
            raise ValueError("Se requiere una lista de tareas y asignaciones.")
        
        # 2. Transformación de Datos (Aplanar el diccionario de asignaciones)
        # Convertimos [{"task": "X", "assignments": {"Rol1": "A"}}] -> DataFrame plano
        normalized_data = []
        all_roles = set()
        
        for _, row in self.df.iterrows():
            task_entry = {"task": row["task"]}
            assignments = row["assignments"]
            
            # Validar valores permitidos (R, A, C, I, o vacío)
            valid_codes = {'R', 'A', 'C', 'I', ''}
            
            for role, code in assignments.items():
                clean_code = code.upper().strip()
                if clean_code not in valid_codes:
                     # Opcional: Lanzar error o ignorar. Aquí lo limpiamos.
                     clean_code = ""
                task_entry[role] = clean_code
                all_roles.add(role)
            
            normalized_data.append(task_entry)
            
        df_raci = pd.DataFrame(normalized_data).fillna("")
        
        # 3. Análisis Horizontal (Por Tarea) - Reglas de Oro
        warnings = []
        
        for _, row in df_raci.iterrows():
            task = row['task']
            # Extraer solo las columnas de roles
            role_values = [row[r] for r in all_roles if r in df_raci.columns]
            
            count_r = role_values.count('R')
            count_a = role_values.count('A')
            
            # Regla 1: Exactamente un A por tarea
            if count_a == 0:
                warnings.append(f"La tarea '{task}' no tiene a nadie que rinda cuentas (Falta 'A').")
            elif count_a > 1:
                warnings.append(f"La tarea '{task}' tiene {count_a} jefes (Múltiples 'A'). Solo debe haber uno.")
                
            # Regla 2: Al menos un R por tarea
            if count_r == 0:
                warnings.append(f"Nadie hace el trabajo en '{task}' (Falta 'R').")

        # 4. Análisis Vertical (Por Rol) - Carga de Trabajo
        role_stats = {}
        for role in all_roles:
            if role in df_raci.columns:
                counts = df_raci[role].value_counts().to_dict()
                role_stats[role] = {
                    "R": counts.get("R", 0),
                    "A": counts.get("A", 0),
                    "C": counts.get("C", 0),
                    "I": counts.get("I", 0)
                }
                
                # Heurística de sobrecarga
                if counts.get("R", 0) == 0 and counts.get("A", 0) == 0:
                     warnings.append(f"El rol '{role}' no tiene responsabilidades asignadas (¿Es necesario?).")

        # 5. Resumen
        status = "Matriz equilibrada." if not warnings else "Se detectaron problemas de asignación."
        summary = (
            f"Matriz RACI analizada ({len(df_raci)} tareas, {len(all_roles)} roles). "
            f"{status} Se encontraron {len(warnings)} advertencias."
        )

        return AnalysisResult(
            tool_name="Matriz de Responsabilidades (RACI)",
            summary=summary,
            chart_data=normalized_data, # La tabla lista para mostrar
            details={
                "warnings": warnings,
                "role_stats": role_stats, # Para gráficas de carga de trabajo
                "roles_detected": list(all_roles)
            }
        )