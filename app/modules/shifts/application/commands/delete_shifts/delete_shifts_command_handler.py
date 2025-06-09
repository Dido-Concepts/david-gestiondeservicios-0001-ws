from mediatr import Mediator
from pydantic import BaseModel

# Importaciones necesarias para la inyección de dependencias y la interfaz del repositorio
from app.constants import injector_var
from app.modules.shifts.domain.repositories.shifts_repository import ShiftsRepository
# Importación de la interfaz base para los manejadores de comandos/queries
from app.modules.share.domain.handler.request_handler import IRequestHandler


class DeleteShiftsCommand(BaseModel):
    """
    Comando que encapsula los datos necesarios para realizar la eliminación
    lógica de un turno.
    Utiliza Pydantic (BaseModel) para la validación automática de datos.
    """
    shift_id: int       # El ID del turno que será marcado como anulado.
    user_modify: str    # El identificador (ej. email) del usuario que realiza la operación.


@Mediator.handler
class DeleteShiftsCommandHandler(IRequestHandler[DeleteShiftsCommand, str]):
    """
    Manejador (Handler) para el comando DeleteShiftsCommand.
    Se encarga de orquestar la lógica para la eliminación lógica de un turno,
    delegando la interacción con la base de datos al repositorio correspondiente.
    """
    def __init__(self) -> None:
        """
        Constructor del manejador.
        Obtiene una instancia del repositorio de turnos (ShiftsRepository)
        a través del inyector de dependencias (injector_var).
        Esto desacopla el manejador de la implementación concreta del repositorio.
        """
        # Obtiene el contenedor de inyección de dependencias.
        injector = injector_var.get()
        # Solicita al contenedor una instancia de ShiftsRepository.
        # El contenedor proporcionará la implementación concreta que haya sido registrada.
        # El '# type: ignore' es para suprimir posibles advertencias del linter sobre
        # obtener una clase abstracta, aunque el inyector devolverá una concreta.
        self.shifts_repository: ShiftsRepository = injector.get(ShiftsRepository)  # type: ignore[type-abstract]

    async def handle(self, command: DeleteShiftsCommand) -> str:
        """
        Lógica principal del manejador para el borrado lógico.
        Se ejecuta cuando el Mediator recibe una instancia de DeleteShiftsCommand.

        Args:
            command (DeleteShiftsCommand): El objeto comando con los datos necesarios
                                         (ID del turno y usuario modificador).

        Returns:
            str: El mensaje de resultado devuelto por la operación del repositorio
                 (ej: "Shift ID 123 for user 5 has been successfully annulled.").
        """
        # Llama al método 'delete_shift' en el repositorio de turnos,
        # que fue implementado para realizar la eliminación lógica.
        # Pasa los datos extraídos del objeto 'command'.
        res: str = await self.shifts_repository.delete_shift(
            shift_id=command.shift_id,        # Pasa el ID del turno a anular
            user_modify=command.user_modify   # Pasa el usuario que realiza la anulación
        )

        # Devuelve el resultado (mensaje de texto) obtenido desde el repositorio.
        return res 