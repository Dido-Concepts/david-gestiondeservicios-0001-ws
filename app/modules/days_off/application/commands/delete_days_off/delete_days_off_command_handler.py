from mediatr import Mediator
from pydantic import BaseModel

# Importaciones necesarias para la inyección de dependencias y la interfaz del repositorio
from app.constants import injector_var
from app.modules.days_off.domain.repositories.days_off_repository import DaysOffRepository
# Importación de la interfaz base para los manejadores de comandos/queries
from app.modules.share.domain.handler.request_handler import IRequestHandler


class DeleteDaysOffCommand(BaseModel):
    """
    Comando que encapsula los datos necesarios para realizar la eliminación
    lógica de un día libre.
    Utiliza Pydantic (BaseModel) para la validación automática de datos.
    """
    day_off_id: int       # El ID del día libre que será marcado como anulado.
    user_modify: str      # El identificador (ej. email) del usuario que realiza la operación.


@Mediator.handler
class DeleteDaysOffCommandHandler(IRequestHandler[DeleteDaysOffCommand, str]):
    """
    Manejador (Handler) para el comando DeleteDaysOffCommand.
    Se encarga de orquestar la lógica para la eliminación lógica de un día libre,
    delegando la interacción con la base de datos al repositorio correspondiente.
    """
    def __init__(self) -> None:
        """
        Constructor del manejador.
        Obtiene una instancia del repositorio de días libres (DaysOffRepository)
        a través del inyector de dependencias (injector_var).
        Esto desacopla el manejador de la implementación concreta del repositorio.
        """
        # Obtiene el contenedor de inyección de dependencias.
        injector = injector_var.get()
        # Solicita al contenedor una instancia de DaysOffRepository.
        # El contenedor proporcionará la implementación concreta que haya sido registrada.
        # El '# type: ignore' es para suprimir posibles advertencias del linter sobre
        # obtener una clase abstracta, aunque el inyector devolverá una concreta.
        self.days_off_repository: DaysOffRepository = injector.get(DaysOffRepository)  # type: ignore[type-abstract]

    async def handle(self, command: DeleteDaysOffCommand) -> str:
        """
        Lógica principal del manejador para el borrado lógico.
        Se ejecuta cuando el Mediator recibe una instancia de DeleteDaysOffCommand.

        Args:
            command (DeleteDaysOffCommand): El objeto comando con los datos necesarios
                                            (ID del día libre y usuario modificador).

        Returns:
            str: El mensaje de resultado devuelto por la operación del repositorio
                 (ej: "Day off ID 123 for user 5 has been successfully annulled.").
        """
        # Llama al método 'delete_day_off' en el repositorio de días libres,
        # que fue implementado para realizar la eliminación lógica.
        # Pasa los datos extraídos del objeto 'command'.
        res: str = await self.days_off_repository.delete_day_off(
            day_off_id=command.day_off_id,      # Pasa el ID del día libre a anular
            user_modify=command.user_modify     # Pasa el usuario que realiza la anulación
        )

        # Devuelve el resultado (mensaje de texto) obtenido desde el repositorio.
        return res 