import re
from datetime import date, time
from typing import Optional
from mediatr import Mediator
from pydantic import BaseModel, field_validator

# Importaciones necesarias del proyecto
from app.constants import injector_var
from app.modules.days_off.domain.repositories.days_off_repository import (
    DaysOffRepository,  # Importa la interfaz del repositorio de días libres
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


# --- Command ---
class UpdateDaysOffCommand(BaseModel):
    """
    Modelo de datos (Command) que representa la solicitud para actualizar un día libre.
    Contiene los datos necesarios y las validaciones de entrada.
    """
    day_off_id: int                                    # ID del día libre a actualizar (identificador)
    user_modify: str                                   # Usuario que realiza la modificación (auditoría)
    tipo_dia_libre_maintable_id: Optional[int] = None # Nuevo tipo de día libre (opcional)
    fecha_inicio: Optional[date] = None                # Nueva fecha de inicio (opcional)
    fecha_fin: Optional[date] = None                   # Nueva fecha de fin (opcional)
    hora_inicio: Optional[time] = None                 # Nueva hora de inicio (opcional)
    hora_fin: Optional[time] = None                    # Nueva hora de fin (opcional)
    motivo: Optional[str] = None                       # Nuevo motivo (opcional)

    @field_validator("user_modify")
    def validate_user_modify(cls, v: str) -> str:
        """Valida que el usuario modificador no esté vacío."""
        if not v or v.isspace():
            raise ValueError("user_modify no puede estar vacío")
        return v.strip()

    @field_validator("fecha_fin")
    def validate_fecha_fin(cls, v: Optional[date], info) -> Optional[date]:
        """Valida que fecha_fin sea posterior o igual a fecha_inicio si ambas están presentes."""
        if v is None:
            return v
        
        fecha_inicio = info.data.get("fecha_inicio")
        if fecha_inicio and v < fecha_inicio:
            raise ValueError("fecha_fin no puede ser anterior a fecha_inicio")
        return v

    @field_validator("hora_fin")
    def validate_hora_fin(cls, v: Optional[time], info) -> Optional[time]:
        """
        Valida que si se proporciona hora_fin, también debe proporcionarse hora_inicio
        y hora_fin debe ser posterior a hora_inicio.
        """
        if v is None:
            return v
        
        hora_inicio = info.data.get("hora_inicio")
        
        # Si se proporciona hora_fin pero no hora_inicio
        if hora_inicio is None:
            raise ValueError("Si se proporciona hora_fin, también debe proporcionarse hora_inicio")
        
        # Si ambas están proporcionadas, hora_fin debe ser > hora_inicio
        if v <= hora_inicio:
            raise ValueError("hora_fin debe ser posterior a hora_inicio")
        
        return v

    @field_validator("hora_inicio")
    def validate_hora_inicio(cls, v: Optional[time], info) -> Optional[time]:
        """
        Valida que si se proporciona hora_inicio, también debe proporcionarse hora_fin.
        """
        if v is None:
            return v
        
        hora_fin = info.data.get("hora_fin")
        
        # Si se proporciona hora_inicio pero no hora_fin
        if hora_fin is None:
            raise ValueError("Si se proporciona hora_inicio, también debe proporcionarse hora_fin")
        
        return v

    @field_validator("motivo")
    def validate_motivo(cls, v: Optional[str]) -> Optional[str]:
        """Valida que motivo no sea solo espacios en blanco si se proporciona."""
        if v is not None and not v.strip():
            raise ValueError("motivo no puede contener solo espacios")
        
        return v.strip() if v else None


# --- Handler ---
@Mediator.handler
class UpdateDaysOffCommandHandler(IRequestHandler[UpdateDaysOffCommand, str]):
    """
    Manejador (Handler) para el comando UpdateDaysOffCommand.
    Orquesta la lógica para actualizar un día libre: recibe el comando validado,
    interactúa con el repositorio y devuelve el resultado.
    """
    def __init__(self) -> None:
        """Inicializa el handler inyectando las dependencias necesarias (el repositorio)."""
        # Obtiene el contenedor de inyección de dependencias
        injector = injector_var.get()
        # Obtiene una instancia concreta del repositorio de días libres
        # El injector sabe qué implementación usar (ej. DaysOffImplementationRepository)
        # gracias a cómo se configuró la inyección de dependencias en otra parte.
        # El type: ignore es porque el injector devuelve 'Any' pero sabemos que es un DaysOffRepository.
        self.days_off_repository: DaysOffRepository = injector.get(DaysOffRepository)  # type: ignore[type-abstract]

    async def handle(self, command: UpdateDaysOffCommand) -> str:
        """
        Ejecuta la lógica principal para manejar el comando de actualización.

        Args:
            command: La instancia del comando UpdateDaysOffCommand con los datos validados.

        Returns:
            Un string con el mensaje de resultado devuelto por el repositorio
            (ej. "Day off ID 123 updated successfully." o un mensaje de error).
        """
        # Llama al método correspondiente en el repositorio para actualizar los detalles
        # Pasa los datos directamente desde el objeto 'command' ya validado por Pydantic.
        result = await self.days_off_repository.update_day_off(
            day_off_id=command.day_off_id,
            user_modify=command.user_modify,
            tipo_dia_libre_maintable_id=command.tipo_dia_libre_maintable_id,
            fecha_inicio=command.fecha_inicio,
            fecha_fin=command.fecha_fin,
            hora_inicio=command.hora_inicio,
            hora_fin=command.hora_fin,
            motivo=command.motivo,
        )

        # Devuelve el resultado (mensaje de texto) que proviene del repositorio
        # (que a su vez, lo obtuvo del stored procedure).
        return result 