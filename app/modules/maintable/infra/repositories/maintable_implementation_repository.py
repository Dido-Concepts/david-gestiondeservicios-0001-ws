from datetime import datetime
from typing import Optional

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# Importaciones del proyecto
from app.constants import uow_var
from app.modules.maintable.domain.entities.maintable_domain import MaintableEntity
from app.modules.maintable.domain.repositories.maintable_repository import MaintableRepository
from app.modules.share.domain.repositories.repository_types import ResponseListRefactor
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error


class MaintableImplementationRepository(MaintableRepository):
    """
    Implementación concreta de la interfaz MaintableRepository usando SQLAlchemy.
    """

    @property
    def _uow(self) -> UnitOfWork:
        """Proporciona acceso a la instancia actual de UnitOfWork."""
        try:
            return uow_var.get()
        except LookupError:
            raise RuntimeError("UnitOfWork no encontrado en el contexto")

    async def get_by_table_name(
        self,
        table_name: str,
        page_index: int,
        page_size: int,
        order_by: str,
        sort_by: str,
        query: Optional[str] = None,
    ) -> ResponseListRefactor[MaintableEntity]:
        stmt = text("""
            SELECT * FROM maintable_get_by_tablename(
                :table_name, :page_index, :page_size, :order_by, :sort_by, :query
            )
        """)

        try:
            result = await self._uow.session.execute(
                stmt,
                {
                    "table_name": table_name,
                    "page_index": page_index,
                    "page_size": page_size,
                    "order_by": order_by,
                    "sort_by": sort_by,
                    "query": query,
                },
            )

            row = result.fetchone()
            if not row:
                return ResponseListRefactor(data=[], total_items=0)

            data_json = row.data  # JSON array de las sedes
            total_items = row.total_items

            # Convertir el JSON a lista de LocationEntity
            maintable_list: list[MaintableEntity] = []

            if data_json:
                for item in data_json:
                    maintable_list.append(MaintableEntity(**item))
            return ResponseListRefactor(data=maintable_list, total_items=total_items)

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")