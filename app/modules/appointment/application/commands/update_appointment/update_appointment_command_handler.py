# update_appointment_command_handler.py

from datetime import datetime

from mediatr import Mediator
from pydantic import BaseModel, ValidationInfo, field_validator

from app.constants import injector_var
from app.modules.appointment.application.utils.appointment_validation_utils import (
    AppointmentValidationUtils,
)
from app.modules.appointment.domain.repositories.appointment_repository import (
    AppointmentRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


# --- Definición del Comando ---
class UpdateAppointmentCommand(BaseModel):
    """
    Comando para solicitar la actualización de una cita existente.
    Utiliza Pydantic para validar los datos de entrada.
    """

    # Campo requerido para identificar la cita
    appointment_id: int

    # Campos requeridos para actualizar una cita
    location_id: int
    user_id: int
    service_id: int
    customer_id: int
    status_maintable_id: int
    start_datetime: datetime
    end_datetime: datetime
    user_modify: str

    @field_validator("end_datetime")
    def validate_datetime_range(cls, v: datetime, info: ValidationInfo) -> datetime:
        """
        Valida que end_datetime sea posterior a start_datetime.
        """
        start_datetime = info.data.get("start_datetime")
        if start_datetime and v <= start_datetime:
            raise ValueError("end_datetime debe ser posterior a start_datetime")
        return v


# --- Definición del Manejador del Comando ---
@Mediator.handler
class UpdateAppointmentCommandHandler(IRequestHandler[UpdateAppointmentCommand, None]):
    """
    Manejador para el comando UpdateAppointmentCommand.
    Orquesta la actualización de una cita utilizando el repositorio correspondiente.
    """

    def __init__(self) -> None:
        # Constructor: Obtiene dependencias usando el inyector
        injector = (
            injector_var.get()
        )  # Obtiene el contenedor de inyección de dependencias

        # Inyecta una instancia del Repositorio de Appointments (la interfaz abstracta)
        # El contenedor se encarga de proporcionar la implementación concreta (PostgresAppointmentRepository)
        self.appointment_repository: AppointmentRepository = injector.get(AppointmentRepository)  # type: ignore[type-abstract]

    async def handle(self, command: UpdateAppointmentCommand) -> None:
        """
        Lógica para manejar el comando UpdateAppointmentCommand.

        Args:
            command: El objeto comando con los datos de la cita a actualizar.

        Raises:
            ValueError: Si ya existe una cita en conflicto con las fechas especificadas.
        """
        # Validar que no exista conflicto de fechas antes de actualizar
        # Se excluye la cita actual del chequeo de conflictos
        await AppointmentValidationUtils.validate_no_conflicting_appointments(
            appointment_repository=self.appointment_repository,
            user_id=command.user_id,
            start_datetime=command.start_datetime,
            end_datetime=command.end_datetime,
            exclude_appointment_id=command.appointment_id,
        )

        # Delega la lógica de actualización al método update_appointment del repositorio
        # Pasa los datos recibidos en el comando al método del repositorio
        await self.appointment_repository.update_appointment(
            appointment_id=command.appointment_id,
            location_id=command.location_id,
            user_id=command.user_id,
            service_id=command.service_id,
            customer_id=command.customer_id,
            status_maintable_id=command.status_maintable_id,
            start_datetime=command.start_datetime,
            end_datetime=command.end_datetime,
            user_modify=command.user_modify,
        )
