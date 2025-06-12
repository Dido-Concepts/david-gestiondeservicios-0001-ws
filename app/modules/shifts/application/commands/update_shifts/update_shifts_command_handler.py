from datetime import date, time
from typing import Optional
from mediatr import Mediator
from pydantic import BaseModel, field_validator, model_validator

# Importaciones necesarias del proyecto
from app.constants import injector_var
from app.modules.shifts.domain.repositories.shifts_repository import (
    ShiftsRepository,  # Importa la interfaz del repositorio de turnos
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


# --- Command ---
class UpdateShiftsCommand(BaseModel):
    """
    Modelo de datos (Command) que representa la solicitud para actualizar un turno.
    Contiene los datos necesarios y las validaciones de entrada.
    """
    shift_id: int                           # ID del turno a actualizar (identificador)
    user_modify: str                        # Usuario que realiza la modificación (auditoría)
    fecha_turno: Optional[date] = None      # Nueva fecha del turno (opcional)
    hora_inicio: Optional[time] = None      # Nueva hora de inicio (opcional)
    hora_fin: Optional[time] = None         # Nueva hora de fin (opcional)

    @field_validator("user_modify")
    def validate_user_modify(cls, v: str) -> str:
        """Valida que el usuario modificador no esté vacío."""
        if not v or v.isspace():
            raise ValueError("user_modify no puede estar vacío")
        return v.strip()

    @model_validator(mode='after')
    def validate_times(self):
        """Valida la lógica entre las horas."""
        # Validar lógica de horas - deben proporcionarse ambas o ninguna
        if (self.hora_inicio is not None) != (self.hora_fin is not None):
            raise ValueError("Si se proporciona hora_inicio u hora_fin, ambas deben proporcionarse")
        
        # Si ambas horas están presentes, hora_fin debe ser posterior a hora_inicio
        if self.hora_inicio is not None and self.hora_fin is not None:
            if self.hora_fin <= self.hora_inicio:
                raise ValueError("hora_fin debe ser posterior a hora_inicio")
        
        return self


# --- Handler ---
@Mediator.handler
class UpdateShiftsCommandHandler(IRequestHandler[UpdateShiftsCommand, str]):
    """
    Manejador (Handler) para el comando UpdateShiftsCommand.
    Orquesta la lógica para actualizar un turno: recibe el comando validado,
    interactúa con el repositorio y devuelve el resultado.
    """
    def __init__(self) -> None:
        """Inicializa el handler inyectando las dependencias necesarias (el repositorio)."""
        # Obtiene el contenedor de inyección de dependencias
        injector = injector_var.get()
        # Obtiene una instancia concreta del repositorio de turnos
        # El injector sabe qué implementación usar (ej. ShiftsImplementationRepository)
        # gracias a cómo se configuró la inyección de dependencias en otra parte.
        # El type: ignore es porque el injector devuelve 'Any' pero sabemos que es un ShiftsRepository.
        self.shifts_repository: ShiftsRepository = injector.get(ShiftsRepository)  # type: ignore[type-abstract]

    async def handle(self, command: UpdateShiftsCommand) -> str:
        """
        Ejecuta la lógica principal para manejar el comando de actualización.

        Args:
            command: La instancia del comando UpdateShiftsCommand con los datos validados.

        Returns:
            Un string con el mensaje de resultado devuelto por el repositorio
            (ej. "Shift ID 123 updated successfully." o un mensaje de error).
        """
        # Llama al método correspondiente en el repositorio para actualizar los detalles
        # Pasa los datos directamente desde el objeto 'command' ya validado por Pydantic.
        result = await self.shifts_repository.update_shift(
            shift_id=command.shift_id,
            user_modify=command.user_modify,
            fecha_turno=command.fecha_turno,
            hora_inicio=command.hora_inicio,
            hora_fin=command.hora_fin,
        )

        # Devuelve el resultado (mensaje de texto) que proviene del repositorio
        # (que a su vez, lo obtuvo del stored procedure).
        return result 