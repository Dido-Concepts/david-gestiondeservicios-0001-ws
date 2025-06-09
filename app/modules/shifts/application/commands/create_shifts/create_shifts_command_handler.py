from datetime import date, time
from mediatr import Mediator  # Importa la biblioteca Mediator
from pydantic import BaseModel  # Importa BaseModel de Pydantic para validación de datos

# Importa la interfaz del repositorio de turnos
from app.modules.shifts.domain.repositories.shifts_repository import ShiftsRepository
# Importa la interfaz base para los manejadores de comandos/solicitudes
from app.modules.share.domain.handler.request_handler import IRequestHandler
# Importa la variable de contexto para el inyector de dependencias
from app.constants import injector_var


# --- Definición del Comando ---
class CreateShiftsCommand(BaseModel):
    """
    Comando para solicitar la creación de un nuevo turno de trabajo.
    Utiliza Pydantic para validar los datos de entrada.
    """
    # Campos requeridos para crear un turno
    user_id: int
    sede_id: int
    fecha_turno: date
    hora_inicio: time
    hora_fin: time
    user_create: str


# --- Definición del Manejador del Comando ---
@Mediator.handler
class CreateShiftsCommandHandler(IRequestHandler[CreateShiftsCommand, str]):
    """
    Manejador para el comando CreateShiftsCommand.
    Orquesta la creación de un turno utilizando el repositorio correspondiente.
    """
    def __init__(self) -> None:
        # Constructor: Obtiene dependencias usando el inyector
        injector = injector_var.get()  # Obtiene el contenedor de inyección de dependencias

        # Inyecta una instancia del Repositorio de Turnos (la interfaz abstracta)
        # El contenedor se encarga de proporcionar la implementación concreta
        self.shifts_repository: ShiftsRepository = injector.get(ShiftsRepository)  # type: ignore[type-abstract]

    async def handle(self, command: CreateShiftsCommand) -> str:
        """
        Lógica para manejar el comando CreateShiftsCommand.

        Args:
            command: El objeto comando con los datos del turno a crear.

        Returns:
            Un mensaje (str) indicando el resultado de la operación.
        """
        # Delega la lógica de creación al método create_shift del repositorio
        # Pasa los datos recibidos en el comando al método del repositorio
        result_message = await self.shifts_repository.create_shift(
            user_id=command.user_id,
            sede_id=command.sede_id,
            fecha_turno=command.fecha_turno,
            hora_inicio=command.hora_inicio,
            hora_fin=command.hora_fin,
            user_create=command.user_create,
        )

        # Devuelve el mensaje obtenido del repositorio
        return result_message 