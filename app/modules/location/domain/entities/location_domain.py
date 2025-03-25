from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class DayOfWeek(Enum):
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miercoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sabado"
    DOMINGO = "Domingo"


@dataclass
class LocationResponse:
    id: int
    nombre_sede: str
    telefono_sede: str
    direccion_sede: str
    insert_date: datetime
    url: Optional[str] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None
