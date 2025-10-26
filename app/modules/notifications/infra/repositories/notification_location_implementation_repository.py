from typing import List, Tuple

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.constants import uow_var
from app.modules.notifications.domain.notification_location_entity import (
    ActiveNotificationLocationEntity,
    LocationNotificationStatusEntity,
)
from app.modules.notifications.domain.repositories.notification_location_repository import (
    NotificationLocationRepository,
)
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error


class NotificationLocationImplementationRepository(NotificationLocationRepository):
    """
    Implementación concreta del repositorio de notification_locations usando SQLAlchemy.
    """

    @property
    def _uow(self) -> UnitOfWork:
        """Proporciona acceso a la instancia actual de UnitOfWork."""
        try:
            return uow_var.get()
        except LookupError:
            raise RuntimeError("UnitOfWork no encontrado en el contexto")

    async def get_all_locations_notification_status(
        self,
    ) -> List[LocationNotificationStatusEntity]:
        """
        Obtiene todas las locations con su estado de notificación.
        """
        try:
            query = text("SELECT * FROM sp_get_all_locations_notification_status()")

            result = await self._uow.session.execute(query)
            rows = result.fetchall()

            return [
                LocationNotificationStatusEntity(
                    location_id=row.location_id,
                    location_name=row.location_name,
                    is_notification_active=row.is_notification_active,
                    notification_location_id=row.notification_location_id,
                )
                for row in rows
            ]

        except DBAPIError as e:
            handle_error(e)
            return []

    async def get_active_notification_locations(
        self,
    ) -> List[ActiveNotificationLocationEntity]:
        """
        Obtiene solo las locations con notificaciones activas.
        """
        try:
            query = text("SELECT * FROM sp_get_active_notification_locations()")

            result = await self._uow.session.execute(query)
            rows = result.fetchall()

            return [
                ActiveNotificationLocationEntity(
                    location_id=row.location_id,
                    location_name=row.location_name,
                    notification_location_id=row.notification_location_id,
                )
                for row in rows
            ]

        except DBAPIError as e:
            handle_error(e)
            return []

    async def upsert_notification_location(
        self, location_id: int, is_active: bool, user_email: str
    ) -> Tuple[int, int, bool, str]:
        """
        Crea o actualiza un registro de notification_location.
        """
        try:
            query = text(
                """
                SELECT * FROM sp_upsert_notification_location(
                    :location_id,
                    :is_active,
                    :user_email
                )
                """
            )

            result = await self._uow.session.execute(
                query,
                {
                    "location_id": location_id,
                    "is_active": is_active,
                    "user_email": user_email,
                },
            )

            row = result.fetchone()

            if not row:
                raise ValueError(
                    "No se pudo crear o actualizar la notification_location"
                )

            return (
                row.notification_location_id,
                row.location_id,
                row.is_active,
                row.action_performed,
            )

        except DBAPIError as e:
            handle_error(e)
            return (0, 0, False, "ERROR")

    async def deactivate_notification_location(
        self, location_id: int, user_email: str
    ) -> Tuple[bool, str]:
        """
        Desactiva las notificaciones para una location.
        """
        try:
            query = text(
                """
                SELECT * FROM sp_deactivate_notification_location(
                    :location_id,
                    :user_email
                )
                """
            )

            result = await self._uow.session.execute(
                query,
                {
                    "location_id": location_id,
                    "user_email": user_email,
                },
            )

            row = result.fetchone()

            if not row:
                return False, "Error al ejecutar la operación"

            return row.success, row.message

        except DBAPIError as e:
            handle_error(e)
            return False, "Error en la base de datos"
