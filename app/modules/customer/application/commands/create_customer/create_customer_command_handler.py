# create_customer_command_handler.py

from typing import Optional
from datetime import date
from mediatr import Mediator  # Importa la biblioteca Mediator
from pydantic import BaseModel  # Importa BaseModel de Pydantic para validación de datos

# Importa la interfaz del repositorio de clientes
from app.modules.customer.application.request.create_customer_request import CustomerStatusEnum
from app.modules.customer.domain.repositories.customer_repository import CustomerRepository
# Importa la interfaz base para los manejadores de comandos/solicitudes
from app.modules.share.domain.handler.request_handler import IRequestHandler
# Importa la variable de contexto para el inyector de dependencias
from app.constants import injector_var


# --- Definición del Comando ---
class CreateCustomerCommand(BaseModel):
    """
    Comando para solicitar la creación de un nuevo cliente.
    Utiliza Pydantic para validar los datos de entrada.
    """
    # Campos requeridos para crear un cliente
    name_customer: str
    user_create: str

    # Campos opcionales
    email_customer: Optional[str] = None
    phone_customer: Optional[str] = None
    birthdate_customer: Optional[date] = None
    status_customer: Optional[CustomerStatusEnum] = 'active'


# --- Definición del Manejador del Comando ---
@Mediator.handler
class CreateCustomerCommandHandler(IRequestHandler[CreateCustomerCommand, int]):
    """
    Manejador para el comando CreateCustomerCommand.
    Orquesta la creación de un cliente utilizando el repositorio correspondiente.
    """
    def __init__(self) -> None:
        # Constructor: Obtiene dependencias usando el inyector
        injector = injector_var.get()  # Obtiene el contenedor de inyección de dependencias

        # Inyecta una instancia del Repositorio de Clientes (la interfaz abstracta)
        # El contenedor se encarga de proporcionar la implementación concreta (PostgresCustomerRepository)
        self.customer_repository: CustomerRepository = injector.get(CustomerRepository)  # type: ignore[type-abstract]

    async def handle(self, command: CreateCustomerCommand) -> int:
        """
        Lógica para manejar el comando CreateCustomerCommand.

        Args:
            command: El objeto comando con los datos del cliente a crear.

        Returns:
            El ID (int) del cliente recién creado.
        """
        # Delega la lógica de creación al método create_customer del repositorio
        # Pasa los datos recibidos en el comando al método del repositorio
        new_customer_id = await self.customer_repository.create_customer(
            name_customer=command.name_customer,
            user_create=command.user_create,
            email_customer=command.email_customer,
            phone_customer=command.phone_customer,
            birthdate_customer=command.birthdate_customer,
            status_customer=command.status_customer.value,
        )

        # Devuelve el ID obtenido del repositorio
        return new_customer_id
