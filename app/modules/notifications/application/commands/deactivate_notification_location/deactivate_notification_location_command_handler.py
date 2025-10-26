from typing import Any, Dict

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.notifications.domain.repositories.notification_location_repository import (
    NotificationLocationRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class DeactivateNotificationLocationCommand(BaseModel):
    """
    Comando para desactivar las notificaciones de una location.
    """

    location_id: int
    user_email: str


@Mediator.handler
class DeactivateNotificationLocationCommandHandler(
    IRequestHandler[DeactivateNotificationLocationCommand, Dict[str, Any]]
):
    """
    Handler para desactivar las notificaciones de una location.
    """

    def __init__(self) -> None:
        injector = injector_var.get()
        self.repository: NotificationLocationRepository = injector.get(NotificationLocationRepository)  # type: ignore[type-abstract]

    async def handle(
        self, command: DeactivateNotificationLocationCommand
    ) -> Dict[str, Any]:
        """
        Maneja el comando para desactivar notification_location.

        Args:
            command: Comando con los datos necesarios

        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        success, message = await self.repository.deactivate_notification_location(
            location_id=command.location_id,
            user_email=command.user_email,
        )

        return {
            "success": success,
            "message": message,
            "location_id": command.location_id,
        }
