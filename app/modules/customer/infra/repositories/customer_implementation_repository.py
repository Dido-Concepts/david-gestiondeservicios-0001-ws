# customer_implementation_repository.py

from typing import Optional
from datetime import date

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# Asumiendo que estas rutas de importación son correctas para tu proyecto
from app.constants import uow_var
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error

# Importa la interfaz abstracta que esta clase implementará
from app.modules.customer.domain.repositories.customer_repository import CustomerRepository


class CustomerImplementationRepository(CustomerRepository):
    """
    Concrete implementation of the CustomerRepository interface using SQLAlchemy
    and a Unit of Work pattern, interacting with a PostgreSQL database.
    """

    @property
    def _uow(self) -> UnitOfWork:
        """Provides access to the current UnitOfWork instance."""
        try:
            # uow_var se asume que es una ContextVar que contiene la UnitOfWork actual
            return uow_var.get()
        except LookupError:
            # Esto ocurre si el repositorio se usa fuera del contexto de una UoW
            # (por ejemplo, fuera de un request de FastAPI si se gestiona por middleware)
            raise RuntimeError("UnitOfWork no encontrado en el contexto")

    async def create_customer(
        self,
        name_customer: str,
        user_create: str,
        email_customer: Optional[str],
        phone_customer: Optional[str],
        birthdate_customer: Optional[date],
        status_customer: Optional[str] = 'active'
    ) -> int:
        """
        Creates a new customer by calling the 'create_customer' stored procedure
        in the PostgreSQL database.

        Args:
            name_customer: The name of the customer (mandatory).
            user_create: The identifier of the user creating the record (mandatory).
            email_customer: The customer's email address (optional).
            phone_customer: The customer's phone number (optional).
            birthdate_customer: The customer's date of birth (optional).
            status_customer: The initial status (optional, defaults to 'active').

        Returns:
            The unique identifier (ID) of the newly created customer.

        Raises:
            Specific exceptions mapped by handle_error (e.g., DuplicateError, ValueError)
            based on the DBAPIError caught.
            RuntimeError: If the UnitOfWork context is not found or if handle_error
                          doesn't raise its own exception (which it should).
        """
        # Llama a la función de PostgreSQL 'create_customer' que definimos antes
        sql_query = """
            SELECT create_customer(
                :p_name_customer,
                :p_email_customer,
                :p_phone_customer,
                :p_birthdate_customer,
                :p_user_create,
                :p_status_customer
            );
        """

        # Mapea los argumentos de la función Python a los parámetros de la consulta SQL
        params = {
            "p_name_customer": name_customer,
            "p_email_customer": email_customer,
            "p_phone_customer": phone_customer,
            "p_birthdate_customer": birthdate_customer,
            "p_user_create": user_create,
            "p_status_customer": status_customer,
        }

        try:
            # Ejecuta la consulta SQL dentro de la sesión de la Unit of Work actual
            result = await self._uow.session.execute(
                text(sql_query),
                params
            )

            # scalar_one() espera exactamente una fila y una columna como resultado
            # (el ID devuelto por la función de PostgreSQL)
            customer_id: int = result.scalar_one()
            return customer_id

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")
