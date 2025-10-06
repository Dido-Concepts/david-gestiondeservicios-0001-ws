# delete_appointment_command_handler.py

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.appointment.domain.repositories.appointment_repository import (
    AppointmentRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


# --- Definición del Comando ---
class DeleteAppointmentCommand(BaseModel):
    """
    Comando para solicitar la anulación (soft delete) de una cita existente.
    Utiliza Pydantic para validar los datos de entrada.
    """

    # Campo requerido para identificar la cita a anular
    appointment_id: int
    user_modify: str


# --- Definición del Manejador del Comando ---
@Mediator.handler
class DeleteAppointmentCommandHandler(IRequestHandler[DeleteAppointmentCommand, None]):
    """
    Manejador para el comando DeleteAppointmentCommand.
    Orquesta la anulación de una cita utilizando el repositorio correspondiente.
    """

    def __init__(self) -> None:
        # Constructor: Obtiene dependencias usando el inyector
        injector = (
            injector_var.get()
        )  # Obtiene el contenedor de inyección de dependencias

        # Inyecta una instancia del Repositorio de Appointments (la interfaz abstracta)
        # El contenedor se encarga de proporcionar la implementación concreta (PostgresAppointmentRepository)
        self.appointment_repository: AppointmentRepository = injector.get(AppointmentRepository)  # type: ignore[type-abstract]

    async def handle(self, command: DeleteAppointmentCommand) -> None:
        """
        Lógica para manejar el comando DeleteAppointmentCommand.

        Args:
            command: El objeto comando con los datos de la cita a anular.

        Raises:
            ValueError: Si la cita no existe.
        """
        # Validar que la cita existe antes de proceder con la anulación
        await self._validate_appointment_exists(command.appointment_id)

        # Delega la lógica de anulación al método annul_appointment del repositorio
        # Pasa los datos recibidos en el comando al método del repositorio
        await self.appointment_repository.annul_appointment(
            appointment_id=command.appointment_id,
            user_modify=command.user_modify,
        )

    async def _validate_appointment_exists(self, appointment_id: int) -> None:
        """
        Valida que la cita exista en la base de datos.
        Usa una búsqueda con rango de fechas amplio para optimizar la consulta.

        Args:
            appointment_id: ID de la cita a validar.

        Raises:
            ValueError: Si la cita no existe.
        """
        # Usar un rango de fechas muy amplio para encontrar la cita
        # Esto es más eficiente que cargar todas las citas
        existing_appointments = (
            await self.appointment_repository.find_appointments_refactor(
                page_index=1,
                page_size=1000,  # Suficiente para encontrar la cita
                order_by="appointment_id",
                sort_by="ASC",
                query=None,
                filters={
                    "start_date": "1900-01-01 00:00:00",  # Fecha muy antigua
                    "end_date": "2100-12-31 23:59:59",  # Fecha muy futura
                },
            )
        )

        # Verificar si existe alguna cita con el ID específico
        appointment_found = any(
            appointment.appointment_id == appointment_id
            for appointment in existing_appointments.data
        )

        if not appointment_found:
            raise ValueError(f"La cita con ID {appointment_id} no existe")
