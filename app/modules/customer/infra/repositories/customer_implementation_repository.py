# customer_implementation_repository.py

from datetime import date, datetime
from typing import Optional, Dict, Any
import json

from fastapi import HTTPException  # Necesario para levantar errores HTTP

# Importaciones de SQLAlchemy y manejo de errores
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# Asumiendo que estas rutas de importación son correctas para tu proyecto
from app.constants import uow_var
from app.modules.customer.domain.entities.customer_domain import CustomerEntity

# Importa la interfaz abstracta que esta clase implementará
from app.modules.customer.domain.repositories.customer_repository import (
    CustomerRepository,
)
from app.modules.share.domain.repositories.repository_types import (
    ResponseList,
    ResponseListRefactor,
)
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error


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
        status_customer: Optional[str] = "active",
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
            raise RuntimeError(
                "Este punto nunca se alcanza"
            )  # handle_error siempre levanta excepción

    async def find_customers(
        self, page_index: int, page_size: int, query: Optional[str] = None
    ) -> (
        "ResponseList[CustomerEntity]"
    ):  # Usamos comillas si ResponseList no está importado globalmente
        """
        Busca clientes de forma paginada llamando a la función almacenada 'get_customers'
        en la base de datos.
        """
        # Importación local si es necesaria y no está global
        from app.modules.share.domain.repositories.repository_types import ResponseList

        # Define la sentencia SQL para llamar a la función PostgreSQL
        stmt = text("SELECT get_customers(:page_index, :page_size, :search_name_query)")
        try:
            # Ejecuta la sentencia
            result = await self._uow.session.execute(
                stmt,
                {
                    "page_index": page_index,
                    "page_size": page_size,
                    "search_name_query": query,
                },
            )
            # Obtiene el resultado JSON devuelto por la función almacenada
            data_dict = result.scalar_one()

            # Procesa la lista de clientes dentro del JSON resultante
            customers_list = []
            for item in data_dict.get("data", []):
                # Parsea fechas/timestamps opcionales de string a objeto Python
                birthdate_str = item.get("birthdate_customer")
                birthdate_obj = (
                    date.fromisoformat(birthdate_str) if birthdate_str else None
                )
                update_date_str = item.get("update_date")
                update_date_obj = (
                    datetime.fromisoformat(update_date_str) if update_date_str else None
                )

                # Crea una instancia de CustomerEntity
                customer = CustomerEntity(
                    id=item["id"],
                    name_customer=item["name_customer"],
                    email_customer=item.get("email_customer"),
                    phone_customer=item.get("phone_customer"),
                    birthdate_customer=birthdate_obj,
                    status_customer=item["status_customer"],
                    insert_date=datetime.fromisoformat(item["insert_date"]),
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
            raise RuntimeError(
                "Este punto nunca se alcanza"
            )  # handle_error siempre levanta excepción

    async def find_customer_refactor(
        self,
        page_index: int,
        page_size: int,
        order_by: str,
        sort_by: str,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> ResponseListRefactor[CustomerEntity]:
        """
        Implementación refactorizada para buscar clientes con paginación.
        Llama al procedimiento almacenado 'customer_get_customers_refactor' en PostgreSQL.
        """
        filters_json = json.dumps(filters) if filters else "{}"

        stmt = text("""
            SELECT * FROM customer_get_customers_refactor(
                :page_index, :page_size, :order_by, :sort_by, :query, CAST(:filters AS JSONB)
            )
        """)

        try:
            result = await self._uow.session.execute(
                stmt,
                {
                    "page_index": page_index,
                    "page_size": page_size,
                    "order_by": order_by,
                    "sort_by": sort_by,
                    "query": query,
                    "filters": filters_json,
                },
            )

            row = result.fetchone()
            if not row:
                return ResponseListRefactor(data=[], total_items=0)

            data_json = row.data  # JSON array de los clientes
            total_items = row.total_items

            # Convertir el JSON a lista de CustomerEntity
            customers_list: list[CustomerEntity] = []

            if data_json:  # Si hay datos
                for item in data_json:
                    # Parsear fechas opcionales
                    birthdate_obj = None
                    if item.get("birthdate_customer"):
                        birthdate_obj = date.fromisoformat(item["birthdate_customer"])

                    update_date_obj = None
                    if item.get("update_date"):
                        update_date_obj = datetime.fromisoformat(item["update_date"])

                    # Crear CustomerEntity
                    customer = CustomerEntity(
                        id=item["id"],
                        name_customer=item["name_customer"],
                        email_customer=item.get("email_customer"),
                        phone_customer=item.get("phone_customer"),
                        birthdate_customer=birthdate_obj,
                        status_customer=item["status_customer"],
                        insert_date=datetime.fromisoformat(item["insert_date"])
                        if item["insert_date"]
                        else datetime.now(),
                        update_date=update_date_obj,
                        user_create=item["user_create"],
                        user_modify=item.get("user_modify"),
                    )

                    customers_list.append(customer)

            return ResponseListRefactor(data=customers_list, total_items=total_items)

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
        user_modify: str,
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
            raise RuntimeError(
                "Este punto nunca se alcanza"
            )  # handle_error siempre levanta excepción

    async def change_status_customer(self, customer_id: int, user_modify: str) -> str:
        """
        Implementación concreta del método para cambiar el estado de un cliente.
        Llama a la función de base de datos 'change_customer_status'
        y devuelve el mensaje resultante.
        """
        # Define la sentencia SQL para llamar a la función PostgreSQL creada anteriormente.
        stmt = text("SELECT change_customer_status(:p_customer_id, :p_user_email)")

        # Prepara el diccionario de parámetros que se pasarán a la consulta.
        params = {
            "p_customer_id": customer_id,
            "p_user_email": user_modify,  # 'user_modify' de Python se mapea a ':p_user_email' en SQL
        }

        try:
            # Ejecuta la función en la base de datos usando la sesión de la Unit of Work.
            result = await self._uow.session.execute(stmt, params)

            # Obtiene el resultado devuelto por la función de base de datos.
            response: str = result.scalar_one()

            # Verifica si la respuesta de la función indica un error conocido.
            if response.startswith("Cliente no encontrado") or response.startswith(
                "Estado actual"
            ):  # Mejorado para capturar ambos errores de SP
                status_code = 404 if "Cliente no encontrado" in response else 400
                raise HTTPException(status_code=status_code, detail=response)

            # Si no es un mensaje de error conocido, se asume éxito
            return response

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError(
                "Este punto nunca se alcanza"
            )  # handle_error siempre levanta excepción

    # --- NUEVO MÉTODO IMPLEMENTADO ---
    async def delete_customer(self, customer_id: int, user_modify: str) -> str:
        """
        Implementación concreta para realizar la eliminación lógica de un cliente.
        Llama a la función de base de datos 'delete_customer' y devuelve
        el mensaje resultante.
        """
        # Define la sentencia SQL para llamar a la función PostgreSQL 'delete_customer'.
        # Usamos nombres de parámetros explícitos (:p_customer_id, :p_user_modifier)
        # que coinciden con los esperados por la función PL/pgSQL creada.
        stmt = text("SELECT delete_customer(:p_customer_id, :p_user_modifier)")

        # Prepara el diccionario de parámetros para la consulta SQL.
        # Mapea los argumentos de Python ('customer_id', 'user_modify') a los
        # nombres esperados en la consulta (:p_customer_id, :p_user_modifier).
        params = {
            "p_customer_id": customer_id,
            "p_user_modifier": user_modify,  # Mapea 'user_modify' al parámetro del SP
        }

        try:
            # Ejecuta la llamada a la función almacenada en la base de datos
            # utilizando la sesión de la Unit of Work actual.
            result = await self._uow.session.execute(stmt, params)

            # Obtiene el mensaje de texto devuelto por la función de PostgreSQL.
            # scalar_one() espera que la función devuelva exactamente una fila y una columna.
            response: str = result.scalar_one()

            # Verifica si la respuesta de la función de base de datos indica un error específico.
            # En este caso, el único error que manejamos explícitamente para levantar HTTPException
            # es cuando el cliente no se encuentra. El mensaje "ya está anulado" se considera informativo.
            if response.startswith("Error: Cliente no encontrado"):
                # Si la función devuelve el error de cliente no encontrado,
                # levantamos una excepción HTTP 404 (Not Found).
                raise HTTPException(status_code=404, detail=response)
            elif response.startswith(
                "Error:"
            ):  # Captura otros errores que empiecen con "Error:"
                # Para otros errores inesperados devueltos por la función que empiecen con "Error:"
                # (aunque el SP actual solo define uno explícito), lanzamos un 400.
                # Podríamos usar 500 si consideramos que son errores internos del SP no previstos.
                raise HTTPException(status_code=400, detail=response)

            # Si la respuesta no indica un error manejado explícitamente (ej. es un mensaje de éxito
            # como "Cliente ... marcado como anulado correctamente" o el informativo
            # "El cliente ... ya se encuentra anulado"), simplemente devolvemos el mensaje.
            return response

        except DBAPIError as e:
            # Captura errores generales de la base de datos (conexión, sintaxis SQL inesperada, etc.)
            # y los maneja usando la función 'handle_error', que probablemente loguea
            # y levanta una excepción HTTP genérica (ej. 500 Internal Server Error).
            handle_error(e)
            # Esta línea teóricamente no se alcanza si handle_error siempre levanta una excepción.
            raise RuntimeError("Este punto nunca se alcanza")


#
