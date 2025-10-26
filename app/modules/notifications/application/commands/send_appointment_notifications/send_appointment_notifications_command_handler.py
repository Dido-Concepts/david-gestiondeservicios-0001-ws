from datetime import datetime
from typing import Any, Dict, List, Optional

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.appointment.domain.entities.appointment_domain import AppointmentEntity
from app.modules.appointment.domain.repositories.appointment_repository import (
    AppointmentRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.whatsapp.infra.services.evolution_api_service import (
    EvolutionApiService,
)


# --- Definición del Comando ---
class SendAppointmentNotificationsCommand(BaseModel):
    """
    Comando para enviar notificaciones de citas por WhatsApp.
    """

    start_date: datetime
    end_date: datetime
    location_id: Optional[int] = None


# --- Definición del Manejador del Comando ---
@Mediator.handler
class SendAppointmentNotificationsCommandHandler(
    IRequestHandler[SendAppointmentNotificationsCommand, Dict[str, Any]]
):
    """
    Manejador para el comando SendAppointmentNotificationsCommand.
    Obtiene las citas en el rango de fechas especificado y envía notificaciones por WhatsApp.
    """

    def __init__(self) -> None:
        """
        Constructor: Inicializa el repositorio de citas y el servicio de WhatsApp.
        """
        injector = injector_var.get()
        self.appointment_repository = injector.get(AppointmentRepository)  # type: ignore[type-abstract]
        self.whatsapp_service = EvolutionApiService()

    async def handle(
        self, command: SendAppointmentNotificationsCommand
    ) -> Dict[str, Any]:
        """
        Lógica para manejar el comando SendAppointmentNotificationsCommand.

        Args:
            command: El objeto comando con los datos del rango de fechas y ubicación.

        Returns:
            Respuesta con el resultado del envío de notificaciones.

        Raises:
            Exception: Si ocurre un error al procesar o enviar las notificaciones.
        """
        try:
            # Preparar filtros para la consulta de citas
            filters: Dict[str, Any] = {
                "start_date": command.start_date.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": command.end_date.strftime("%Y-%m-%d %H:%M:%S"),
            }

            if command.location_id:
                filters["location_id"] = command.location_id

            # Obtener las citas usando el repositorio de appointments
            appointments_result = (
                await self.appointment_repository.find_appointments_refactor(
                    page_index=1,
                    page_size=100,
                    order_by="start_datetime",
                    sort_by="ASC",
                    query=None,
                    filters=filters,
                )
            )

            appointments = appointments_result.data
            sent_notifications = 0
            failed_notifications = 0
            notification_results: List[Dict[str, Any]] = []

            # Procesar cada cita y enviar notificación
            for appointment in appointments:
                try:
                    # Construir el mensaje de notificación
                    message = self._build_notification_message(appointment)

                    # Enviar mensaje directamente usando el servicio de WhatsApp
                    await self.whatsapp_service.send_text_message(
                        number=f"51{appointment.customer_phone}",
                        text=message,
                        delay=None,
                        link_preview=False,
                    )

                    # El servicio devuelve directamente la respuesta, consideramos éxito si no hay excepción
                    sent_notifications += 1
                    notification_results.append(
                        {
                            "appointment_id": appointment.appointment_id,
                            "customer_name": appointment.customer_name,
                            "customer_phone": appointment.customer_phone,
                            "status": "sent",
                            "message": "Notificación enviada exitosamente",
                        }
                    )

                except Exception as e:
                    failed_notifications += 1
                    notification_results.append(
                        {
                            "appointment_id": appointment.appointment_id,
                            "customer_name": getattr(
                                appointment, "customer_name", "Desconocido"
                            ),
                            "customer_phone": getattr(
                                appointment, "customer_phone", "Sin teléfono"
                            ),
                            "status": "failed",
                            "message": f"Error al procesar: {str(e)}",
                        }
                    )

            return {
                "success": True,
                "message": f"Proceso completado. {sent_notifications} enviadas, {failed_notifications} fallidas",
                "data": {
                    "total_appointments": len(appointments),
                    "sent_notifications": sent_notifications,
                    "failed_notifications": failed_notifications,
                    "results": notification_results,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error al procesar notificaciones: {str(e)}",
                "data": None,
            }

    def _build_notification_message(self, appointment: AppointmentEntity) -> str:
        """
        Construye el mensaje de notificación para la cita.

        Args:
            appointment: Objeto con los datos de la cita.

        Returns:
            str: Mensaje formateado para WhatsApp.
        """
        # Formatear la fecha de la cita
        start_datetime_str = appointment.start_datetime.strftime("%d/%m/%Y a las %H:%M")

        message = f"""
🗓️ *Recordatorio de Cita*

Hola {appointment.customer_name},

Tienes una cita programada:

📅 *Fecha y Hora:* {start_datetime_str}
📍 *Ubicación:* {appointment.location_name}
👨‍💼 *Con:* {appointment.user_name}
✂️ *Servicio:* {appointment.service_name}
💰 *Precio:* ${appointment.service_price}
⏱️ *Duración:* {appointment.service_duration} minutos

Por favor, llega puntualmente. Si necesitas reprogramar o cancelar, contáctanos con anticipación.

¡Te esperamos! 😊
        """.strip()

        return message
