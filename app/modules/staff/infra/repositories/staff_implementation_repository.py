# staff_implementation_repository.py

import json
from datetime import datetime
from typing import Any, Dict, Optional

# Importaciones de SQLAlchemy y manejo de errores
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# Asumiendo que estas rutas de importación son correctas para tu proyecto
from app.constants import uow_var
from app.modules.share.domain.repositories.repository_types import ResponseListRefactor
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error
from app.modules.staff.domain.entities.staff_domain import RoleEntity, StaffEntity

# Importa la interfaz abstracta que esta clase implementará
from app.modules.staff.domain.repositories.staff_repository import StaffRepository


class StaffImplementationRepository(StaffRepository):
    """
    Implementación concreta de la interfaz StaffRepository usando SQLAlchemy
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

    async def find_staff_refactor(
        self,
        page_index: int,
        page_size: int,
        order_by: str,
        sort_by: str,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> ResponseListRefactor[StaffEntity]:
        """
        Implementación concreta del método para buscar staff con paginación refactorizada.
        Llama al stored procedure 'staff_get_all' de PostgreSQL.

        Args:
            page_index: Índice de la página.
            page_size: Tamaño de la página.
            order_by: Campo por el cual ordenar.
            sort_by: Dirección del ordenamiento ('ASC' o 'DESC').
            query: Término de búsqueda opcional.
            filters: Diccionario opcional con filtros.

        Returns:
            ResponseListRefactor[StaffEntity]: Lista paginada de staff.
        """
        # Sentencia SQL que llama al stored procedure
        stmt = text(
            """
            SELECT data, total_items
            FROM staff_get_all(
                :p_page_index, :p_page_size, :p_order_by, :p_sort_by, :p_query, :p_filters
            )
            """
        )

        # Preparar filtros como JSON
        filters_json = json.dumps(filters) if filters else "{}"

        # Diccionario con los parámetros para la función SQL
        params = {
            "p_page_index": page_index,
            "p_page_size": page_size,
            "p_order_by": order_by,
            "p_sort_by": sort_by,
            "p_query": query,
            "p_filters": filters_json,
        }

        try:
            # Ejecuta la llamada a la función dentro de la sesión de la UoW
            result = await self._uow.session.execute(stmt, params)
            # Obtiene la fila con data y total_items
            row = result.fetchone()

            if row is None:
                # Si no hay resultados, devuelve una lista vacía
                return ResponseListRefactor(data=[], total_items=0)

            # Extrae los datos JSON y el total de items
            data_json = row[0]  # El campo 'data' del SP
            total_items = row[1]  # El campo 'total_items' del SP

            staff_list = []

            # Procesa la lista de staff dentro del JSON resultante
            if data_json:  # Si hay datos
                for item in data_json:
                    # Parsear fechas
                    created_at = (
                        datetime.fromisoformat(item["created_at"])
                        if item.get("created_at")
                        else datetime.now()
                    )

                    updated_at_obj = None
                    if item.get("updated_at"):
                        updated_at_obj = datetime.fromisoformat(item["updated_at"])

                    # Parsear roles
                    roles_list = []
                    if item.get("roles"):
                        for role_item in item["roles"]:
                            role = RoleEntity(
                                role_id=role_item["role_id"],
                                role_name=role_item["role_name"],
                            )
                            roles_list.append(role)

                    # Crear StaffEntity
                    staff = StaffEntity(
                        id=item["id"],
                        user_name=item["user_name"],
                        email=item["email"],
                        status=item["status"],
                        location_id=item["location_id"],
                        location_name=item["location_name"],
                        roles=roles_list,
                        created_at=created_at,
                        updated_at=updated_at_obj,
                    )

                    staff_list.append(staff)

            return ResponseListRefactor(data=staff_list, total_items=total_items)

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")
