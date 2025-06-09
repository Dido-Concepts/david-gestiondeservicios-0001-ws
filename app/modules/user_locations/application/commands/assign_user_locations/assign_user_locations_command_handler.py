# assign_user_locations_command_handler.py

# Importaciones necesarias para el mediador y la validación de datos del comando
from mediatr import Mediator
from pydantic import BaseModel # Para definir la estructura y validación del comando

# Importa la interfaz del repositorio de asignaciones usuario-ubicación.
# ¡¡¡IMPORTANTE!!! Ajusta la siguiente ruta de importación según dónde hayas guardado
# el archivo user_locations_repository.py que definimos anteriormente.
# Ejemplo de ruta (ajusta según tu estructura de proyecto):
from app.modules.user_locations.domain.repositories.user_locations_repository import UserLocationsRepository
# (Si tu módulo para esto se llama 'assignments' o similar, ajusta la ruta,
#  ej: from app.modules.assignments.domain.repositories.user_locations_repository import UserLocationsRepository)

# Importa la interfaz base para los manejadores de comandos (si la usas consistentemente)
from app.modules.share.domain.handler.request_handler import IRequestHandler
# Importa la variable de contexto para el inyector de dependencias (si así gestionas tus dependencias)
from app.constants import injector_var


# --- Definición del Comando ---
class AssignUserToLocationCommand(BaseModel):
    """
    Comando para solicitar la asignación de un usuario a una sede/ubicación.
    Utiliza Pydantic (BaseModel) para asegurar que los datos de entrada
    tengan la estructura y tipos correctos.
    """
    # Campos requeridos para la asignación, basados en los parámetros del SP
    user_id: int          # El ID del usuario que se va a asignar.
    sede_id: int          # El ID de la sede/ubicación a la que se asignará el usuario.
    user_transaction: str # Identificador del usuario o sistema que realiza esta operación (para auditoría).


# --- Definición del Manejador del Comando ---
@Mediator.handler
class AssignUserToLocationCommandHandler(IRequestHandler[AssignUserToLocationCommand, str]):
    """
    Manejador para el comando AssignUserToLocationCommand.
    Este manejador es responsable de orquestar la acción de asignar un usuario
    a una sede/ubicación. Utiliza el UserLocationsRepository para interactuar
    con la capa de persistencia (que a su vez llama al SP).
    El tipo de retorno es 'str' porque el repositorio (y el SP) devuelven un mensaje textual.
    """
    def __init__(self) -> None:
        """
        Constructor del manejador.
        Aquí es donde se obtienen las dependencias, como el repositorio.
        Se asume el uso de un contenedor de inyección de dependencias (injector).
        """
        injector = injector_var.get() # Obtiene el contenedor de inyección de dependencias.

        # Se solicita al inyector una instancia de UserLocationsRepository.
        # El inyector se encarga de proporcionar la implementación concreta
        # (por ejemplo, UserLocationsImplementationRepository que creamos antes).
        self.user_locations_repository: UserLocationsRepository = injector.get(UserLocationsRepository) # type: ignore[type-abstract]

    async def handle(self, command: AssignUserToLocationCommand) -> str:
        """
        Lógica principal para manejar el comando AssignUserToLocationCommand.
        Este método es invocado por el sistema Mediator cuando se envía un
        comando de este tipo.

        Args:
            command: El objeto comando que contiene los datos necesarios para la asignación
                     (user_id, sede_id, user_transaction).

        Returns:
            Un mensaje de texto (str) que indica el resultado de la operación de asignación
            (ej. "Nueva asignación creada...", "Asignación reactivada...", etc.),
            el cual es devuelto por el repositorio (que lo obtiene del SP).
        """
        # En una aplicación más compleja, aquí podrías tener lógica de negocio adicional
        # antes de llamar al repositorio. Por ejemplo:
        # - Verificar si el 'user_transaction' tiene permisos para realizar esta asignación.
        # - Validar reglas de negocio que no estén cubiertas por el SP o la base de datos.
        # Sin embargo, para este caso, el SP 'sp_assign_user_to_location' ya maneja
        # la lógica de datos principal (crear si no existe, reactivar si estaba inactivo, etc.).

        # Se delega la operación de asignación al método correspondiente del repositorio,
        # pasando los datos contenidos en el 'command'. 
        result_message = await self.user_locations_repository.assign_user_to_location(
            user_id=command.user_id,
            sede_id=command.sede_id,
            user_transaction=command.user_transaction
        )

        # Se devuelve el mensaje de resultado que proporcionó el repositorio.
        return result_message