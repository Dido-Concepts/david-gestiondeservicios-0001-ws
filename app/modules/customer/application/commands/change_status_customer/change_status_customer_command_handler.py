from mediatr import Mediator
from pydantic import BaseModel

# Importaciones necesarias para la inyección de dependencias y la interfaz del repositorio
from app.constants import injector_var
from app.modules.customer.domain.repositories.customer_repository import CustomerRepository
# Importación de la interfaz base para los manejadores de comandos/queries
from app.modules.share.domain.handler.request_handler import IRequestHandler


class ChangeStatusCustomerCommand(BaseModel):
    """
    Comando que encapsula los datos necesarios para cambiar el estado de un cliente.
    Utiliza Pydantic (BaseModel) para la validación automática de datos.
    """
    customer_id: int      # El ID del cliente cuyo estado se modificará.
    user_modify: str      # El identificador (ej. email) del usuario que realiza la operación.


@Mediator.handler
class ChangeStatusCustomerCommandHandler(IRequestHandler[ChangeStatusCustomerCommand, str]):
    """
    Manejador (Handler) para el comando ChangeStatusCustomerCommand.
    Se encarga de orquestar la lógica para cambiar el estado de un cliente,
    delegando la interacción con la base de datos al repositorio correspondiente.
    """
    def __init__(self) -> None:
        """
        Constructor del manejador.
        Obtiene una instancia del repositorio de clientes (CustomerRepository)
        a través del inyector de dependencias (injector_var).
        Esto desacopla el manejador de la implementación concreta del repositorio.
        """
        injector = injector_var.get()
        # Obtiene la implementación concreta registrada para CustomerRepository
        self.customer_repository: CustomerRepository = injector.get(CustomerRepository)  # type: ignore[type-abstract]

    async def handle(self, command: ChangeStatusCustomerCommand) -> str:
        """
        Lógica principal del manejador.
        Se ejecuta cuando el Mediator recibe una instancia de ChangeStatusCustomerCommand.

        Args:
            command (ChangeStatusCustomerCommand): El objeto comando con los datos necesarios.

        Returns:
            str: El mensaje de resultado devuelto por la operación del repositorio
                 (ej: "Estado del cliente cambiado a activo").
        """
        # Llama al método correspondiente en el repositorio de clientes,
        # pasando los datos extraídos del comando.
        res: str = await self.customer_repository.change_status_customer(
            customer_id=command.customer_id,      # Pasa el ID del cliente
            user_modify=command.user_modify       # Pasa el usuario que modifica
        )

        # Devuelve el resultado obtenido del repositorio.
        return res
