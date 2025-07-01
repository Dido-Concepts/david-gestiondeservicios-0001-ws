from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ServiceEntity:
    service_id: int
    service_name: str
    category_id: int
    duration_minutes: Optional[float]
    price: float
    description: Optional[str]
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]


@dataclass
class ServiceEntity2:
    """
    Entidad extendida para servicios que incluye información de categoría y sede
    Utilizada para endpoints v2 que requieren información completa
    """

    service_id: int
    service_name: str
    duration_minutes: Optional[float]
    price: float
    description: Optional[str]
    category_id: int
    category_name: str
    category_description: Optional[str]
    sede_id: int
    sede_name: str
    sede_telefono: Optional[str]
    sede_direccion: Optional[str]
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]
