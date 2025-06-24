from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from app.modules.share.domain.file.file_domain import FileEntity, FileResponse


class DayOfWeek(Enum):
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miercoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sabado"
    DOMINGO = "Domingo"


@dataclass
class ScheduleRangeDomain:
    start: str
    end: str


@dataclass
class ScheduleRequestDomain:
    day: DayOfWeek
    ranges: list[ScheduleRangeDomain]


@dataclass
class LocationResponse:
    id: int
    nombre_sede: str
    telefono_sede: str
    direccion_sede: str
    insert_date: datetime
    location_review: str
    status: bool
    url: Optional[str] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None


@dataclass
class LocationInfoResponse:
    id: int
    nombre_sede: str
    telefono_sede: str
    direccion_sede: str
    location_review: str
    insert_date: datetime
    file: FileResponse
    schedules: list[ScheduleRequestDomain]
    status: bool


@dataclass
class SedeDomain:
    id: int
    nombre_sede: str
    telefono_sede: Optional[str]
    direccion_sede: Optional[str]
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]
    file_id: Optional[int]
    review_location: str
    status: bool


@dataclass
class LocationEntity:
    id: int
    nombre_sede: str
    telefono_sede: Optional[str]
    direccion_sede: Optional[str]
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]
    review_location: str
    status: bool
    file: FileEntity
