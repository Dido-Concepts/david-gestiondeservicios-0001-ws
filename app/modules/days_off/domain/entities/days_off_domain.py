from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date, time


@dataclass
class DaysOffEntity:
    """
    Entidad de dominio que representa un registro de día libre de la base de datos.
    Corresponde a las columnas de la tabla 'days_off'.
    """
    id: int
    user_id: int
    tipo_dia_libre_maintable_id: int
    fecha_inicio: date
    fecha_fin: date
    hora_inicio: Optional[time]
    hora_fin: Optional[time]
    motivo: Optional[str]
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]
    annulled: bool 