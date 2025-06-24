from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from app.modules.user.domain.models.user_enum import Status


class EventType(Enum):
    SHIFT = "SHIFT"
    DAY_OFF = "DAY_OFF"


@dataclass
class UserLocationEntity:
    """
    Entidad de dominio que representa la relación entre un usuario y una sede.
    Corresponde a la tabla 'user_locations' de la base de datos.
    """
    id: int
    user_id: int
    sede_id: int
    annulled: bool
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]


@dataclass
class UserLocationResponse:
    """
    Entidad de respuesta que incluye información básica de la relación usuario-sede
    con datos adicionales del usuario y la sede.
    """
    id: int
    user_id: int
    user_name: str
    user_email: str
    user_status: Status
    sede_id: int
    sede_name: str
    sede_address: Optional[str]
    sede_phone: Optional[str]
    assigned_date: datetime
    is_active: bool


@dataclass
class UserLocationDetailResponse:
    """
    Entidad de respuesta detallada que incluye información completa
    del usuario, sede y su relación.
    """
    id: int
    user_id: int
    user_name: str
    user_email: str
    user_status: Status
    user_created_at: datetime
    sede_id: int
    sede_name: str
    sede_address: Optional[str]
    sede_phone: Optional[str]
    sede_review: str
    sede_status: bool
    assigned_date: datetime
    last_updated: Optional[datetime]
    assigned_by: str
    modified_by: Optional[str]
    is_active: bool


@dataclass
class UserEventEntity:
    """
    Entidad que representa un evento (turno o día libre) de un usuario.
    Utilizada en conjunto con UserLocationEventEntity.
    """
    event_type: EventType
    event_id: int
    event_start_time: datetime
    event_end_time: datetime
    event_description: str
    event_sede_id: Optional[int] = None


@dataclass
class UserLocationEventEntity:
    """
    Entidad que combina información de usuario con sus eventos (turnos y días libres)
    para una sede específica. Resultado del SP 'user_locations_get_user_by_location'.
    """
    user_id: int
    user_name: str
    email: str
    event_type: Optional[str] = None
    event_id: Optional[int] = None
    event_start_time: Optional[datetime] = None
    event_end_time: Optional[datetime] = None
    event_description: Optional[str] = None
    event_sede_id: Optional[int] = None


@dataclass
class UserLocationSummaryResponse:
    """
    Entidad de respuesta resumida para mostrar estadísticas
    de usuarios por sede en un período específico.
    """
    sede_id: int
    sede_name: str
    total_users: int
    active_users: int
    users_with_shifts: int
    users_with_days_off: int
    total_events: int


@dataclass
class AssignUserToLocationRequest:
    """
    Entidad de request para asignar un usuario a una sede.
    """
    user_id: int
    sede_id: int
    user_create: str


@dataclass
class UpdateUserLocationRequest:
    """
    Entidad de request para actualizar la asignación de un usuario a una sede.
    """
    user_location_id: int
    user_modify: str
    annulled: Optional[bool] = None


@dataclass
class UserLocationFilterRequest:
    """
    Entidad de request para filtrar asignaciones de usuarios a sedes.
    """
    sede_id: Optional[int] = None
    user_id: Optional[int] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None 