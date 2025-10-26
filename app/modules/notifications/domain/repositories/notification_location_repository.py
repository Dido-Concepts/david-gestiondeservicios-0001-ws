from abc import ABC, abstractmethod
from typing import List, Tuple

from app.modules.notifications.domain.notification_location_entity import (
    ActiveNotificationLocationEntity,
    LocationNotificationStatusEntity,
)


class NotificationLocationRepository(ABC):
    """
    Repositorio abstracto para manejar las operaciones de notification_locations.
    """

    @abstractmethod
    async def get_all_locations_notification_status(
        self,
    ) -> List[LocationNotificationStatusEntity]:
        """
        Obtiene todas las locations con su estado de notificación.

        Returns:
            List[LocationNotificationStatusEntity]: Lista de locations con su estado.
        """
        pass

    @abstractmethod
    async def get_active_notification_locations(
        self,
    ) -> List[ActiveNotificationLocationEntity]:
        """
        Obtiene solo las locations con notificaciones activas.

        Returns:
            List[ActiveNotificationLocationEntity]: Lista de locations activas.
        """
        pass

    @abstractmethod
    async def upsert_notification_location(
        self, location_id: int, is_active: bool, user_email: str
    ) -> Tuple[int, int, bool, str]:
        """
        Crea o actualiza un registro de notification_location.

        Args:
            location_id: ID de la location
            is_active: Estado de activación
            user_email: Email del usuario que realiza la operación

        Returns:
            Tuple[int, int, bool, str]: (notification_location_id, location_id, is_active, action_performed)
        """
        pass

    @abstractmethod
    async def deactivate_notification_location(
        self, location_id: int, user_email: str
    ) -> Tuple[bool, str]:
        """
        Desactiva las notificaciones para una location.

        Args:
            location_id: ID de la location
            user_email: Email del usuario que realiza la operación

        Returns:
            Tuple[bool, str]: (success, message)
        """
        pass
