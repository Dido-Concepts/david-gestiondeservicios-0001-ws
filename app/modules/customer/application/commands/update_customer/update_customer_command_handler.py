# update_customer_command_handler.py

import re
from datetime import date
from mediatr import Mediator
from pydantic import BaseModel, field_validator, EmailStr

# Importaciones necesarias del proyecto
from app.constants import injector_var
from app.modules.customer.domain.repositories.customer_repository import (
    CustomerRepository,  # Importa la interfaz del repositorio de cliente
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


# --- Command ---
class UpdateCustomerCommand(BaseModel):
    """
    Modelo de datos (Command) que representa la solicitud para actualizar un cliente.
    Contiene los datos necesarios y las validaciones de entrada.
    """
    customer_id: int        # ID del cliente a actualizar (identificador)
    name_customer: str      # Nuevo nombre del cliente
    email_customer: EmailStr  # Nuevo email del cliente (EmailStr valida el formato)
    phone_customer: str     # Nuevo teléfono del cliente
    birthdate_customer: date  # Nueva fecha de nacimiento del cliente
    user_modify: str        # Usuario que realiza la modificación (auditoría)

    @field_validator("name_customer")
    def validate_name_customer(cls, v: str) -> str:
        """Valida que el nombre no contenga caracteres especiales no permitidos."""
        if not v or v.isspace():
            raise ValueError("name_customer no puede estar vacío")
        # Permite letras (con acentos/ñ), números y espacios. Ajusta si necesitas otros.
        if not re.match(r"^[A-ZÁÉÍÓÚÜÑa-záéíóúüñ0-9 ]+$", v):
            raise ValueError("name_customer contiene caracteres no permitidos")
        return v.strip()  # Quita espacios al inicio/final

    @field_validator("phone_customer")
    def validate_phone_customer(cls, v: str) -> str:
        """Valida el formato del número de teléfono."""
        if not v or v.isspace():
            raise ValueError("phone_customer no puede estar vacío")
        # Ejemplo de validación: permite números, '+', '-', '(', ')', espacios, hasta 30 chars.
        # Adapta esta regex según los formatos de teléfono que quieras permitir.
        if not re.match(r"^[0-9+\-() ]{5,30}$", v):
            raise ValueError("phone_customer tiene un formato inválido o longitud incorrecta")
        return v.strip()

    # No se necesita un validador explícito para birthdate_customer si se confía
    # en la conversión automática de Pydantic a 'date'. Se podría añadir lógica
    # si se quisiera validar que la fecha no sea futura, por ejemplo.

    @field_validator("user_modify")
    def validate_user_modify(cls, v: str) -> str:
        """Valida que el usuario modificador no esté vacío."""
        if not v or v.isspace():
            raise ValueError("user_modify no puede estar vacío")
        return v.strip()


# --- Handler ---
@Mediator.handler
class UpdateCustomerCommandHandler(IRequestHandler[UpdateCustomerCommand, str]):
    """
    Manejador (Handler) para el comando UpdateCustomerCommand.
    Orquesta la lógica para actualizar un cliente: recibe el comando validado,
    interactúa con el repositorio y devuelve el resultado.
    """
    def __init__(self) -> None:
        """Inicializa el handler inyectando las dependencias necesarias (el repositorio)."""
        # Obtiene el contenedor de inyección de dependencias
        injector = injector_var.get()
        # Obtiene una instancia concreta del repositorio de clientes
        # El injector sabe qué implementación usar (ej. CustomerImplementationRepository)
        # gracias a cómo se configuró la inyección de dependencias en otra parte.
        # El type: ignore es porque el injector devuelve 'Any' pero sabemos que es un CustomerRepository.
        self.customer_repository: CustomerRepository = injector.get(CustomerRepository)  # type: ignore[type-abstract]

    async def handle(self, command: UpdateCustomerCommand) -> str:
        """
        Ejecuta la lógica principal para manejar el comando de actualización.

        Args:
            command: La instancia del comando UpdateCustomerCommand con los datos validados.

        Returns:
            Un string con el mensaje de resultado devuelto por el repositorio
            (ej. "Cliente actualizado correctamente." o un mensaje de error).
        """
        # Llama al método correspondiente en el repositorio para actualizar los detalles
        # Pasa los datos directamente desde el objeto 'command' ya validado por Pydantic.
        result = await self.customer_repository.update_details_customer(
            customer_id=command.customer_id,
            name_customer=command.name_customer,
            email_customer=str(command.email_customer),  # Convierte EmailStr a str para el repo
            phone_customer=command.phone_customer,
            birthdate_customer=command.birthdate_customer,
            user_modify=command.user_modify,
        )

        # Devuelve el resultado (mensaje de texto) que proviene del repositorio
        # (que a su vez, lo obtuvo del stored procedure).
        return result