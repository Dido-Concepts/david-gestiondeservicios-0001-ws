from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from mediatr import Mediator

from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)
from app.modules.notifications.application.commands.send_appointment_notifications.send_appointment_notifications_command_handler import (
    SendAppointmentNotificationsCommand,
)
from app.modules.notifications.application.request.send_appointment_notifications_request import (
    SendAppointmentNotificationsRequest,
)


class NotificationsV2Controller:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:

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
                                            "message": "Notificación enviada exitosamente"
                                        }
                                    ]
                                }
                            }
                        }
                    },
                },
                400: {"description": "Error en los datos enviados"},
                500: {"description": "Error interno del servidor"},
            },
        )(self.send_appointment_notifications)

    async def send_appointment_notifications(
        self, request: SendAppointmentNotificationsRequest
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
            raise HTTPException(
                status_code=500, 
                detail=f"Error interno: {str(e)}"
            )