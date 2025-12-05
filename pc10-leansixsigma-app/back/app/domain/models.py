from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import JSON, Column, Text

# -----------------------------------------------------------------------------
# TABLA 1: PROJECTS (Proyectos)
# -----------------------------------------------------------------------------
class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=200)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    status: str = Field(default="In Progress")
    current_phase: str = Field(default="Define")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relaciones (No crean columnas en la BD, son para Python)
    analyses: List["Analysis"] = Relationship(back_populates="project")
    datasets: List["Dataset"] = Relationship(back_populates="project")


# -----------------------------------------------------------------------------
# TABLA 2: DATASETS (Datos Crudos)
# -----------------------------------------------------------------------------
class Dataset(SQLModel, table=True):
    __tablename__ = "datasets"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    
    name: str = Field(..., description="Nombre del archivo o lote")
    description: Optional[str] = None
    
    # Guardamos los datos crudos (lista de diccionarios) como JSON
    raw_data: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relaciones
    project: Optional[Project] = Relationship(back_populates="datasets")
    used_in_analyses: List["Analysis"] = Relationship(back_populates="dataset")


# -----------------------------------------------------------------------------
# TABLA 3: ANALYSES (Resultados de Herramientas)
# -----------------------------------------------------------------------------
class Analysis(SQLModel, table=True):
    __tablename__ = "analyses"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    dataset_id: Optional[int] = Field(default=None, foreign_key="datasets.id")
    
    tool_name: str
    dmaic_phase: str
    title: Optional[str] = Field(default=None)
    
    # Inputs y Outputs guardados como JSON
    input_params: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    result_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    user_notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    project: Optional[Project] = Relationship(back_populates="analyses")
    dataset: Optional[Dataset] = Relationship(back_populates="used_in_analyses")