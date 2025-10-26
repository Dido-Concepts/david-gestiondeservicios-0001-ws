from typing import List

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.notifications.domain.notification_location_entity import (
    ActiveNotificationLocationEntity,
)
from app.modules.notifications.domain.repositories.notification_location_repository import (
    NotificationLocationRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class GetActiveNotificationLocationsQuery(BaseModel):
    """
    Query para obtener solo las locations con notificaciones activas.
    """

    pass


@Mediator.handler
class GetActiveNotificationLocationsQueryHandler(
    IRequestHandler[
        GetActiveNotificationLocationsQuery, List[ActiveNotificationLocationEntity]
    ]
):
    """
    Handler para obtener solo las locations con notificaciones activas.
    """

    def __init__(self) -> None:
        injector = injector_var.get()
        self.repository: NotificationLocationRepository = injector.get(NotificationLocationRepository)  # type: ignore[type-abstract]

    async def handle(
        self, query: GetActiveNotificationLocationsQuery
    ) -> List[ActiveNotificationLocationEntity]:
        """
        Maneja la consulta para obtener las locations con notificaciones activas.

        Args:
            query: Query con los parámetros de búsqueda

        Returns:
            List[ActiveNotificationLocationEntity]: Lista de locations activas
        """
        return await self.repository.get_active_notification_locations()
