from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from mediatr import Mediator

from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_current_user,
    permission_required,
)
from app.modules.notifications.application.commands.deactivate_notification_location.deactivate_notification_location_command_handler import (
    DeactivateNotificationLocationCommand,
)

# Importar todos los handlers para que se registren en MediatR
from app.modules.notifications.application.commands.send_appointment_notifications.send_appointment_notifications_command_handler import (
    SendAppointmentNotificationsCommand,
)
from app.modules.notifications.application.commands.upsert_notification_location.upsert_notification_location_command_handler import (
    UpsertNotificationLocationCommand,
)
from app.modules.notifications.application.queries.get_active_notification_locations.get_active_notification_locations_query_handler import (
    GetActiveNotificationLocationsQuery,
)
from app.modules.notifications.application.queries.get_all_locations_notification_status.get_all_locations_notification_status_query_handler import (
    GetAllLocationsNotificationStatusQuery,
)
from app.modules.notifications.application.request.notification_location_requests import (
    DeactivateNotificationLocationRequest,
    UpsertNotificationLocationRequest,
)
from app.modules.notifications.application.request.send_appointment_notifications_request import (
    SendAppointmentNotificationsRequest,
)
from app.modules.notifications.domain.notification_location_entity import (
    ActiveNotificationLocationEntity,
    LocationNotificationStatusEntity,
)


class NotificationsV2Controller:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.get(
            "/notifications/locations",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                200: {
                    "description": "Lista de todas las locations con su estado de notificación",
                    "content": {
                        "application/json": {
                            "example": [
                                {
                                    "location_id": 1,
                                    "location_name": "Sede Principal",
                                    "is_notification_active": True,
                                    "notification_location_id": 5,
                                }
                            ]
                        }
                    },
                }
            },
        )(self.get_all_locations_notification_status)

        self.router.post(
            "/notifications/locations",
            dependencies=[Depends(permission_required(roles=["admin"]))],
            responses={
                200: {
                    "description": "Configuración de notificación activada/desactivada exitosamente",
                    "content": {
                        "application/json": {
                            "example": {
                                "notification_location_id": 5,
                                "location_id": 1,
                                "is_active": True,
                                "action_performed": "UPDATED",
                            }
                        }
                    },
                }
            },
        )(self.upsert_notification_location)

        self.router.get(
            "/notifications/locations/active",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                200: {
                    "description": "Lista de locations con notificaciones activas",
                    "content": {
                        "application/json": {
                            "example": [
                                {
                                    "location_id": 1,
                                    "location_name": "Sede Principal",
                                    "notification_location_id": 5,
                                }
                            ]
                        }
                    },
                }
            },
        )(self.get_active_notification_locations)

        self.router.delete(
            "/notifications/locations",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                200: {
                    "description": "Notificación desactivada exitosamente",
                    "content": {
                        "application/json": {
                            "example": {
                                "success": True,
                                "message": "Notificación desactivada correctamente",
                                "location_id": 1,
                            }
                        }
                    },
                }
            },
        )(self.deactivate_notification_location)

        self.router.post(
            "/notifications/send-appointment-notifications",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                200: {
                    "description": "Notificaciones enviadas exitosamente",
                    "content": {
                        "application/json": {
                            "example": {
                                "success": True,
                                "message": "Proceso completado. 3 enviadas, 0 fallidas",
                                "data": {
                                    "total_appointments": 3,
                                    "sent_notifications": 3,
                                    "failed_notifications": 0,
                                    "results": [
                                        {
                                            "appointment_id": 1,
                                            "customer_name": "Juan Pérez",
                                            "customer_phone": "987654321",
                                            "status": "sent",
                                            "message": "Notificación enviada exitosamente",
                                        }
                                    ],
                                },
                            }
                        }
                    },
                },
                400: {"description": "Error en los datos enviados"},
                500: {"description": "Error interno del servidor"},
            },
        )(self.send_appointment_notifications)

    async def get_all_locations_notification_status(
        self,
    ) -> List[LocationNotificationStatusEntity]:
        """
        Obtiene todas las locations con su estado de notificación.

        Retorna una lista con todas las sedes/locations disponibles
        e indica cuáles tienen las notificaciones activas y cuáles no.
        Útil para mostrar un listado con switches/checkboxes en el frontend.
        """
        query = GetAllLocationsNotificationStatusQuery()
        result: List[LocationNotificationStatusEntity] = await self.mediator.send_async(
            query
        )
        return result

    async def get_active_notification_locations(
        self,
    ) -> List[ActiveNotificationLocationEntity]:
        """
        Obtiene solo las locations que tienen las notificaciones activas.

        Retorna únicamente las sedes/locations que están configuradas
        para recibir notificaciones. Útil para procesos internos que
        necesitan saber qué locations notificar.
        """
        query = GetActiveNotificationLocationsQuery()
        result: List[ActiveNotificationLocationEntity] = await self.mediator.send_async(
            query
        )
        return result

    async def upsert_notification_location(
        self,
        request: UpsertNotificationLocationRequest,
        current_user: UserAuth = Depends(get_current_user),
    ) -> Dict[str, Any]:
        """
        Activa o desactiva las notificaciones para una location específica.

        Si no existe un registro para la location, lo crea.
        Si ya existe, actualiza su estado (activo/inactivo).

        Campos requeridos:
        - location_id: ID de la location/sede
        - is_active: true para activar, false para desactivar

        Esta operación es perfecta para manejar el estado de un switch/checkbox
        en el frontend donde el usuario puede activar/desactivar notificaciones
        por location.
        """

        if not current_user.email:
            raise ValueError("User email not found in token")

        command = UpsertNotificationLocationCommand(
            location_id=request.location_id,
            is_active=request.is_active,
            user_email=current_user.email,
        )

        result: Dict[str, Any] = await self.mediator.send_async(command)
        return result

    async def deactivate_notification_location(
        self,
        request: DeactivateNotificationLocationRequest,
        current_user: UserAuth = Depends(get_current_user),
    ) -> Dict[str, Any]:
        """
        Desactiva las notificaciones para una location específica.

        Este endpoint está diseñado para desactivar explícitamente
        las notificaciones de una location. Es una alternativa al
        endpoint upsert con is_active=false.

        Campos requeridos:
        - location_id: ID de la location/sede a desactivar
        """
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = DeactivateNotificationLocationCommand(
            location_id=request.location_id,
            user_email=current_user.email,
        )

        result: Dict[str, Any] = await self.mediator.send_async(command)
        return result

    async def send_appointment_notifications(
        self,
        request: SendAppointmentNotificationsRequest,
        current_user: UserAuth = Depends(get_current_user),
    ) -> Dict[str, Any]:
        """
        Envía notificaciones de WhatsApp para las citas en el rango de fechas especificado
        """
        try:
            # Crear el comando usando MediatR
            command = SendAppointmentNotificationsCommand(
                start_date=request.start_date,
                end_date=request.end_date,
                location_id=request.location_id,
            )

            # Enviar el comando usando el mediador
            result: Dict[str, Any] = await self.mediator.send_async(command)

            if result.get("success"):
                return result
            else:
                raise HTTPException(
                    status_code=500,
                    detail=result.get("message", "Error al enviar notificaciones"),
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
