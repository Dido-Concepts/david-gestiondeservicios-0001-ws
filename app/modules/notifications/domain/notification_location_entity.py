from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NotificationLocationEntity:
    """
    Entidad de dominio que representa la configuración de notificaciones por location.
    """

    id: int
    location_id: int
    is_active: bool
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]
    annulled: bool


@dataclass
class LocationNotificationStatusEntity:
    """
    Entidad que representa el estado de notificación de una location con información adicional.
    """

    location_id: int
    location_name: str
    is_notification_active: bool
    notification_location_id: Optional[int]


@dataclass
class ActiveNotificationLocationEntity:
    """
    Entidad que representa las locations con notificaciones activas.
    """

    location_id: int
    location_name: str
    notification_location_id: int
