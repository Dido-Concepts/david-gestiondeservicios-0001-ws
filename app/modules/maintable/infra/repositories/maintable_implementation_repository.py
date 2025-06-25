from datetime import datetime
from typing import Optional, List, Tuple

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# Importaciones del proyecto
from app.constants import uow_var
from app.modules.maintable.domain.entities.maintable_domain import MaintableEntity
from app.modules.maintable.domain.repositories.maintable_repository import MaintableRepository
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

    async def get_by_criteria(
        self,
        table_name: str,
        page_index: int,
        page_size: int,
        query: Optional[str],
        sort_by: str,
        order: str
    ) -> Tuple[List[MaintableEntity], int]:
        """
        Obtiene registros de la tabla de mantenimiento llamando al stored
        procedure 'maintable_sp_get_by_criteria' en la base de datos.
        """
        # --- AJUSTE CRÍTICO PARA LA PAGINACIÓN ---
        # El API usa un índice 1-based (amigable para usuarios).
        # El SP probablemente espera 0-based para los cálculos de OFFSET.
        # Aquí hacemos la traducción: restamos 1.
        db_page_index = page_index - 1

        stmt = text("""
            SELECT maintable_sp_get_by_criteria(
                :p_table_name, :p_query, :p_sort_by, 
                :p_order, :p_page_size, :p_page_index
            )
        """)
        # --- LÍNEA DE DEPURACIÓN CRÍTICA ---
        # Este es el diccionario de parámetros que se envían
        params = {
            "p_table_name": table_name,
            "p_query": query,
            "p_sort_by": sort_by,
            "p_order": order,
            "p_page_size": page_size,
            "p_page_index": db_page_index 
        }
        # --- LÍNEA DE DEPURACIÓN CRÍTICA ---
        print("DEBUG: Llamando a maintable_sp_get_by_criteria con:")
        print(params)
        # ------------------------------------
        
        try:
            result = await self._uow.session.execute(
                stmt,
                {
                    "p_table_name": table_name,
                    "p_query": query,
                    "p_sort_by": sort_by,
                    "p_order": order,
                    "p_page_size": page_size,
                    "p_page_index": page_index
                },
            )
            
            # Asumimos que el SP devuelve un único resultado JSON.
            data_dict = result.scalar_one_or_none()

            # Si no hay resultados, devolvemos una tupla vacía y limpia.
            if not data_dict or not data_dict.get("data"):
                return [], 0

            # --- REFINAMIENTO CLAVE ---
            # Usamos una list comprehension con desempaquetado de diccionario (**)
            # para crear las entidades de forma limpia y robusta.
            # Esto funciona si las claves del JSON del SP coinciden con los campos del dataclass.
            maintable_list = [
                MaintableEntity(**item) for item in data_dict.get("data", [])
            ]

            total_count = data_dict.get("total_count", 0)

            # Devolvemos la tupla simple que define nuestro contrato de repositorio.
            return maintable_list, total_count
            
        except DBAPIError as e:
            handle_error(e)
            # handle_error debería levantar una excepción, por lo que este punto no se alcanza.
            # Se añade por completitud y para satisfacer al linter.
            raise