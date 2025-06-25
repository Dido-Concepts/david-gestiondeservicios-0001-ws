"""
Este módulo contiene schemas Pydantic compartidos y reutilizables
a través de diferentes módulos de la aplicación.
"""
from pydantic import BaseModel, Field
from typing import List, Any, Dict

class MetaSchema(BaseModel):
    """Define la estructura de los metadatos de paginación."""
    page_index: int = Field(..., description="Índice de la página actual.")
    page_size: int = Field(..., description="Número de registros por página.")
    page_count: int = Field(..., description="Número total de páginas disponibles.")
    total: int = Field(..., description="Número total de registros que coinciden con la consulta.")


class PaginatedResponse(BaseModel):
    """
    Define la estructura estándar para todas las respuestas de API paginadas.
    Es un sobre que contiene los metadatos y los datos.
    """
    meta: MetaSchema
    
    # Usamos List[Dict[str, Any]] para que este modelo sea genérico y pueda
    # contener cualquier tipo de dato, ya sea completo o moldeado por el DataShaper.
    data: List[Dict[str, Any]]