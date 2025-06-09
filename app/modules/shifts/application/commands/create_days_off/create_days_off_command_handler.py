from typing import Optional
from datetime import date, time
from mediatr import Mediator  # Importa la biblioteca Mediator
from pydantic import BaseModel  # Importa BaseModel de Pydantic para validación de datos

# Importa la interfaz del repositorio de días libres
from app.modules.days_off.domain.repositories.days_off_repository import DaysOffRepository
# Importa la interfaz base para los manejadores de comandos/solicitudes
from app.modules.share.domain.handler.request_handler import IRequestHandler
# Importa la variable de contexto para el inyector de dependencias
from app.constants import injector_var


# --- Definición del Comando ---
class CreateDaysOffCommand(BaseModel):
    """
    Comando para solicitar la creación de un nuevo período de día libre.
    Utiliza Pydantic para validar los datos de entrada.
    """
    # Campos requeridos para crear un día libre
    user_id: int
    tipo_dia_libre_maintable_id: int
    fecha_inicio: date
    fecha_fin: date
    user_create: str

    # Campos opcionales
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    motivo: Optional[str] = None


# --- Definición del Manejador del Comando ---
@Mediator.handler
class CreateDaysOffCommandHandler(IRequestHandler[CreateDaysOffCommand, str]):
    """
    Manejador para el comando CreateDaysOffCommand.
    Orquesta la creación de un día libre utilizando el repositorio correspondiente.
    """
    def __init__(self) -> None:
        # Constructor: Obtiene dependencias usando el inyector
        injector = injector_var.get()  # Obtiene el contenedor de inyección de dependencias

        # Inyecta una instancia del Repositorio de Días Libres (la interfaz abstracta)
        # El contenedor se encarga de proporcionar la implementación concreta
        self.days_off_repository: DaysOffRepository = injector.get(DaysOffRepository)  # type: ignore[type-abstract]

    async def handle(self, command: CreateDaysOffCommand) -> str:
        """
        Lógica para manejar el comando CreateDaysOffCommand.

        Args:
            command: El objeto comando con los datos del día libre a crear.

        Returns:
            Un mensaje (str) indicando el resultado de la operación.
        """
        # Delega la lógica de creación al método create_day_off del repositorio
        # Pasa los datos recibidos en el comando al método del repositorio
        result_message = await self.days_off_repository.create_day_off(
            user_id=command.user_id,
            tipo_dia_libre_maintable_id=command.tipo_dia_libre_maintable_id,
            fecha_inicio=command.fecha_inicio,
            fecha_fin=command.fecha_fin,
            user_create=command.user_create,
            hora_inicio=command.hora_inicio,
            hora_fin=command.hora_fin,
            motivo=command.motivo,
        )

        # Devuelve el mensaje obtenido del repositorio
        return result_message 