# customer_implementation_repository.py

from typing import Optional
from datetime import date, datetime

# Importaciones de SQLAlchemy y manejo de errores
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from fastapi import HTTPException  # Necesario para levantar errores HTTP

# Asumiendo que estas rutas de importación son correctas para tu proyecto
from app.constants import uow_var
from app.modules.customer.domain.entities.customer_domain import CustomerEntity
from app.modules.share.domain.repositories.repository_types import ResponseList
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error

# Importa la interfaz abstracta que esta clase implementará
from app.modules.customer.domain.repositories.customer_repository import CustomerRepository


class CustomerImplementationRepository(CustomerRepository):
    """
    Implementación concreta de la interfaz CustomerRepository usando SQLAlchemy
    y un patrón Unit of Work, interactuando con una base de datos PostgreSQL.
    Esta clase contiene el código real para interactuar con la base de datos.
    """

    @property
    def _uow(self) -> UnitOfWork:
        """Proporciona acceso a la instancia actual de UnitOfWork."""
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
        Crea un nuevo cliente llamando al procedimiento almacenado 'create_customer'
        en la base de datos PostgreSQL.
        """
        # Llama a la función de PostgreSQL 'create_customer'
        sql_query = """
            SELECT create_customer(
                :p_name_customer, :p_email_customer, :p_phone_customer,
                :p_birthdate_customer, :p_user_create, :p_status_customer
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
            result = await self._uow.session.execute(text(sql_query), params)
            # scalar_one() espera exactamente una fila y una columna (el ID)
            customer_id: int = result.scalar_one()
            return customer_id
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def find_customers(
        self, page_index: int, page_size: int
    ) -> 'ResponseList[CustomerEntity]':  # Usamos comillas si ResponseList no está importado globalmente
        """
        Busca clientes de forma paginada llamando a la función almacenada 'get_customers'
        en la base de datos.
        """
        # Importación local si es necesaria y no está global
        from app.modules.share.domain.repositories.repository_types import ResponseList

        # Define la sentencia SQL para llamar a la función PostgreSQL
        stmt = text("SELECT get_customers(:page_index, :page_size)")
        try:
            # Ejecuta la sentencia
            result = await self._uow.session.execute(
                stmt,
                {"page_index": page_index, "page_size": page_size, },
            )
            # Obtiene el resultado JSON devuelto por la función almacenada
            data_dict = result.scalar_one()

            # Procesa la lista de clientes dentro del JSON resultante
            customers_list = []
            for item in data_dict.get("data", []):
                # Parsea fechas/timestamps opcionales de string a objeto Python
                birthdate_str = item.get("birthdate_customer")
                birthdate_obj = date.fromisoformat(birthdate_str) if birthdate_str else None
                update_date_str = item.get("update_date")
                update_date_obj = datetime.fromisoformat(update_date_str) if update_date_str else None
                insert_date_str = item.get("insert_date")
                insert_date_obj = datetime.fromisoformat(insert_date_str) if insert_date_str else None

                # Crea una instancia de CustomerEntity
                customer = CustomerEntity(
                    id=item["id"],
                    name_customer=item["name_customer"],
                    email_customer=item.get("email_customer"),
                    phone_customer=item.get("phone_customer"),
                    birthdate_customer=birthdate_obj,
                    status_customer=item["status_customer"],
                    insert_date=insert_date_obj,
                    update_date=update_date_obj,
                    user_create=item["user_create"],
                    user_modify=item.get("user_modify"),
                )
                customers_list.append(customer)

            # Construye el objeto ResponseList
            response = ResponseList(
                data=customers_list,
                total_items=data_dict.get("total_items", 0),
                total_pages=data_dict.get("total_pages", 0),
            )
            return response
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def update_details_customer(
        self,
        customer_id: int,
        name_customer: str,
        email_customer: str,
        phone_customer: str,
        birthdate_customer: date,
        user_modify: str
    ) -> str:
        """
        Implementación concreta para actualizar los detalles de un cliente.
        Llama al stored procedure 'update_customer_details' en PostgreSQL.
        """
        # Sentencia SQL que llama a la función de PostgreSQL
        stmt = text(
            """
            SELECT update_customer_details(
                :p_customer_id, :p_name_customer, :p_email_customer,
                :p_phone_customer, :p_birthdate_customer, :p_user_modify
            )
            """
        )

        # Diccionario con los parámetros para la función SQL
        params = {
            "p_customer_id": customer_id,
            "p_name_customer": name_customer,
            "p_email_customer": email_customer,
            "p_phone_customer": phone_customer,
            "p_birthdate_customer": birthdate_customer,
            "p_user_modify": user_modify,
        }

        try:
            # Ejecuta la llamada a la función dentro de la sesión de la UoW
            result = await self._uow.session.execute(stmt, params)
            # Obtiene el mensaje de texto devuelto por la función
            response: str = result.scalar_one()

            # Verifica si la respuesta indica un error conocido devuelto por la función
            if response.startswith("Error:"):
                if "No se encontró el cliente" in response:
                    # Si el cliente no existe, lanza un error HTTP 404 (Not Found)
                    raise HTTPException(status_code=404, detail=response)
                elif "ya existe para otro cliente" in response:
                    # Si el email está duplicado, lanza un error HTTP 409 (Conflict) o 400 (Bad Request)
                    raise HTTPException(status_code=409, detail=response)
                else:
                    # Para otros errores definidos en la función SQL, lanza un error HTTP 400 (Bad Request)
                    raise HTTPException(status_code=400, detail=response)

            # Si no empieza con "Error:", asume éxito y devuelve el mensaje
            return response

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    # --- MÉTODO IMPLEMENTADO ---
    async def change_status_customer(self, customer_id: int, user_modify: str) -> str:
        """
        Implementación concreta del método para cambiar el estado de un cliente.
        Llama a la función de base de datos 'change_customer_status'
        y devuelve el mensaje resultante.
        """
        # Define la sentencia SQL para llamar a la función PostgreSQL creada anteriormente.
        # Usamos nombres de parámetros explícitos (:p_customer_id, :p_user_email)
        # que coinciden con los esperados por la función PL/pgSQL.
        stmt = text("SELECT change_customer_status(:p_customer_id, :p_user_email)")

        # Prepara el diccionario de parámetros que se pasarán a la consulta.
        # Mapea los argumentos de la función Python ('customer_id', 'user_modify')
        # a los nombres esperados por la consulta SQL (:p_customer_id, :p_user_email).
        params = {
            "p_customer_id": customer_id,
            "p_user_email": user_modify,  # 'user_modify' de Python se mapea a ':p_user_email' en SQL
        }

        try:
            # Ejecuta la función en la base de datos usando la sesión de la Unit of Work.
            # Pasa la sentencia SQL y los parámetros.
            result = await self._uow.session.execute(stmt, params)

            # Obtiene el resultado devuelto por la función de base de datos.
            # scalar_one() espera que la función devuelva exactamente una fila y una columna (el mensaje TEXT).
            response: str = result.scalar_one()

            # Verifica si la respuesta de la función indica un error conocido.
            # Basado en la función PL/pgSQL, un mensaje común de error es "Cliente no encontrado..."
            if response.startswith("Cliente no encontrado") or response.startswith("Estado actual desconocido"):
                # Si el cliente no se encontró u ocurrió otro error definido en la función,
                # lanza una excepción HTTP 404 (Not Found) o 400 (Bad Request) para notificar al cliente de la API.
                # Usamos 404 si es "no encontrado", podríamos usar 400 para otros errores como "estado desconocido".
                status_code = 404 if "Cliente no encontrado" in response else 400
                raise HTTPException(status_code=status_code, detail=response)

            # Si no es un mensaje de error conocido, se asume que la operación fue exitosa
            # y se devuelve el mensaje tal cual (ej: "Estado del cliente cambiado a bloqueado").
            return response

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")
