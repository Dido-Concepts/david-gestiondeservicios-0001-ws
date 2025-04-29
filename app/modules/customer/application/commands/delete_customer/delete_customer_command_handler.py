from mediatr import Mediator
from pydantic import BaseModel

# Importaciones necesarias para la inyección de dependencias y la interfaz del repositorio
from app.constants import injector_var
from app.modules.customer.domain.repositories.customer_repository import CustomerRepository
# Importación de la interfaz base para los manejadores de comandos/queries
from app.modules.share.domain.handler.request_handler import IRequestHandler


class DeleteCustomerCommand(BaseModel):
    """
    Comando que encapsula los datos necesarios para realizar la eliminación
    lógica de un cliente.
    Utiliza Pydantic (BaseModel) para la validación automática de datos.
    """
    customer_id: int      # El ID del cliente que será marcado como anulado.
    user_modify: str      # El identificador (ej. email) del usuario que realiza la operación.


@Mediator.handler
class DeleteCustomerCommandHandler(IRequestHandler[DeleteCustomerCommand, str]):
    """
    Manejador (Handler) para el comando DeleteCustomerCommand.
    Se encarga de orquestar la lógica para la eliminación lógica de un cliente,
    delegando la interacción con la base de datos al repositorio correspondiente.
    """
    def __init__(self) -> None:
        """
        Constructor del manejador.
        Obtiene una instancia del repositorio de clientes (CustomerRepository)
        a través del inyector de dependencias (injector_var).
        Esto desacopla el manejador de la implementación concreta del repositorio.
        """
        # Obtiene el contenedor de inyección de dependencias.
        injector = injector_var.get()
        # Solicita al contenedor una instancia de CustomerRepository.
        # El contenedor proporcionará la implementación concreta que haya sido registrada.
        # El '# type: ignore' es para suprimir posibles advertencias del linter sobre
        # obtener una clase abstracta, aunque el inyector devolverá una concreta.
        self.customer_repository: CustomerRepository = injector.get(CustomerRepository)  # type: ignore[type-abstract]

    async def handle(self, command: DeleteCustomerCommand) -> str:
        """
        Lógica principal del manejador para el borrado lógico.
        Se ejecuta cuando el Mediator recibe una instancia de DeleteCustomerCommand.

        Args:
            command (DeleteCustomerCommand): El objeto comando con los datos necesarios
                                             (ID del cliente y usuario modificador).

        Returns:
            str: El mensaje de resultado devuelto por la operación del repositorio
                 (ej: "Cliente con ID: X marcado como anulado correctamente.").
        """
        # Llama al método 'delete_customer' en el repositorio de clientes,
        # que fue implementado para realizar la eliminación lógica.
        # Pasa los datos extraídos del objeto 'command'.
        res: str = await self.customer_repository.delete_customer(
            customer_id=command.customer_id,    # Pasa el ID del cliente a anular
            user_modify=command.user_modify     # Pasa el usuario que realiza la anulación
        )

        # Devuelve el resultado (mensaje de texto) obtenido desde el repositorio.
        return res