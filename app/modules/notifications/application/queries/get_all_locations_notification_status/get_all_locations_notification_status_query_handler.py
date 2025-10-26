from typing import List

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.notifications.domain.notification_location_entity import (
    LocationNotificationStatusEntity,
)
from app.modules.notifications.domain.repositories.notification_location_repository import (
    NotificationLocationRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class GetAllLocationsNotificationStatusQuery(BaseModel):
    """
    Query para obtener todas las locations con su estado de notificación.
    """

    pass


@Mediator.handler
class GetAllLocationsNotificationStatusQueryHandler(
    IRequestHandler[
        GetAllLocationsNotificationStatusQuery, List[LocationNotificationStatusEntity]
    ]
):
    """
    Handler para obtener todas las locations con su estado de notificación.
    """

    def __init__(self) -> None:
        injector = injector_var.get()
        self.repository: NotificationLocationRepository = injector.get(NotificationLocationRepository)  # type: ignore[type-abstract]

    async def handle(
        self, query: GetAllLocationsNotificationStatusQuery
    ) -> List[LocationNotificationStatusEntity]:
        """
        Maneja la consulta para obtener todas las locations con su estado de notificación.

        Args:
            query: Query con los parámetros de búsqueda

        Returns:
            List[LocationNotificationStatusEntity]: Lista de locations con su estado
        """
        return await self.repository.get_all_locations_notification_status()
