# create_appointment_command_handler.py

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
class CreateAppointmentCommand(BaseModel):
    """
    Comando para solicitar la creación de una nueva cita.
    Utiliza Pydantic para validar los datos de entrada.
    """

    # Campos requeridos para crear una cita
    location_id: int
    user_id: int
    service_id: int
    customer_id: int
    status_maintable_id: int
    start_datetime: datetime
    end_datetime: datetime
    user_create: str

    @field_validator("end_datetime")
    def validate_datetime_range(cls, v: datetime, info: ValidationInfo) -> datetime:
        """
        Valida que end_datetime sea posterior a start_datetime.
        """
        start_datetime = info.data.get("start_datetime")
        if start_datetime and v <= start_datetime:
            raise ValueError("end_datetime debe ser posterior a start_datetime")
        return v

    @field_validator("start_datetime")
    def validate_start_datetime_future(cls, v: datetime) -> datetime:
        """
        Valida que start_datetime sea en el futuro.
        """
        if v <= datetime.now():
            raise ValueError("start_datetime debe ser una fecha y hora futura")
        return v


# --- Definición del Manejador del Comando ---
@Mediator.handler
class CreateAppointmentCommandHandler(IRequestHandler[CreateAppointmentCommand, int]):
    """
    Manejador para el comando CreateAppointmentCommand.
    Orquesta la creación de una cita utilizando el repositorio correspondiente.
    """

    def __init__(self) -> None:
        # Constructor: Obtiene dependencias usando el inyector
        injector = (
            injector_var.get()
        )  # Obtiene el contenedor de inyección de dependencias

        # Inyecta una instancia del Repositorio de Appointments (la interfaz abstracta)
        # El contenedor se encarga de proporcionar la implementación concreta (PostgresAppointmentRepository)
        self.appointment_repository: AppointmentRepository = injector.get(AppointmentRepository)  # type: ignore[type-abstract]

    async def handle(self, command: CreateAppointmentCommand) -> int:
        """
        Lógica para manejar el comando CreateAppointmentCommand.

        Args:
            command: El objeto comando con los datos de la cita a crear.

        Returns:
            El ID (int) de la cita recién creada.

        Raises:
            ValueError: Si ya existe una cita en conflicto con las fechas especificadas.
        """
        # Validar que no exista conflicto de fechas antes de crear
        await AppointmentValidationUtils.validate_no_conflicting_appointments(
            appointment_repository=self.appointment_repository,
            user_id=command.user_id,
            start_datetime=command.start_datetime,
            end_datetime=command.end_datetime,
        )

        # Delega la lógica de creación al método create_appointment del repositorio
        # Pasa los datos recibidos en el comando al método del repositorio
        new_appointment_id = await self.appointment_repository.create_appointment(
            location_id=command.location_id,
            user_id=command.user_id,
            service_id=command.service_id,
            customer_id=command.customer_id,
            status_maintable_id=command.status_maintable_id,
            start_datetime=command.start_datetime,
            end_datetime=command.end_datetime,
            user_create=command.user_create,
        )

        # Devuelve el ID obtenido del repositorio
        return new_appointment_id
