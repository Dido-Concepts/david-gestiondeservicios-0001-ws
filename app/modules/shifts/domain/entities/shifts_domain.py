from dataclasses import dataclass
from datetime import datetime, date, time
from typing import Optional


@dataclass
class ShiftsEntity:
    """
    Entidad de dominio que representa un turno de trabajo de la base de datos.
    Corresponde a las columnas de la tabla 'shifts'.
    """
    id: int
    user_id: int
    sede_id: int
    fecha_turno: date
    hora_inicio: time
    hora_fin: time
    user_create: str
    annulled: bool
    insert_date: datetime
    user_modify: Optional[str] = None
    update_date: Optional[datetime] = None


@dataclass
class UserLocationEventEntity:
    """
    Entidad de dominio que representa el resultado del stored procedure
    'user_locations_get_user_by_location', que combina información de usuarios
    con sus eventos (turnos y días libres) para una sede específica.
    """
    user_id: int
    user_name: str
    email: str
    event_type: Optional[str] = None        # 'SHIFT' o 'DAY_OFF' o None si no tiene eventos
    event_id: Optional[int] = None
    event_start_time: Optional[datetime] = None
    event_end_time: Optional[datetime] = None
    event_description: Optional[str] = None
    event_sede_id: Optional[int] = None


@dataclass
class ShiftDetailEntity:
    """
    Entidad de dominio que representa un turno con información detallada
    incluyendo datos relacionados (usuario y sede).
    """
    shift_id: int
    user_id: int
    user_name: str
    user_email: str
    sede_id: int
    sede_name: str
    fecha_turno: date
    hora_inicio: time
    hora_fin: time
    start_datetime: datetime
    end_datetime: datetime
    user_create: str
    annulled: bool
    insert_date: datetime
    user_modify: Optional[str] = None
    update_date: Optional[datetime] = None
