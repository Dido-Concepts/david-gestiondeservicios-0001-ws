from typing import Any, Dict

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.notifications.domain.repositories.notification_location_repository import (
    NotificationLocationRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class UpsertNotificationLocationCommand(BaseModel):
    """
    Comando para crear o actualizar una configuración de notificación por location.
    """

    location_id: int
    is_active: bool
    user_email: str


@Mediator.handler
class UpsertNotificationLocationCommandHandler(
    IRequestHandler[UpsertNotificationLocationCommand, Dict[str, Any]]
):
    """
    Handler para crear o actualizar una configuración de notificación por location.
    """

    def __init__(self) -> None:
        injector = injector_var.get()
        self.repository: NotificationLocationRepository = injector.get(NotificationLocationRepository)  # type: ignore[type-abstract]

    async def handle(
        self, command: UpsertNotificationLocationCommand
    ) -> Dict[str, Any]:
        """
        Maneja el comando para crear o actualizar notification_location.

        Args:
            command: Comando con los datos necesarios

        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        (
            notification_location_id,
            location_id,
            is_active,
            action_performed,
        ) = await self.repository.upsert_notification_location(
            location_id=command.location_id,
            is_active=command.is_active,
            user_email=command.user_email,
        )

        return {
            "notification_location_id": notification_location_id,
            "location_id": location_id,
            "is_active": is_active,
            "action_performed": action_performed,
        }
