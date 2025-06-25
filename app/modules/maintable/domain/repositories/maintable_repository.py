from abc import ABC, abstractmethod
from typing import Optional

# Importaciones específicas del módulo
from app.modules.maintable.domain.entities.maintable_domain import MaintableEntity
from app.modules.share.domain.repositories.repository_types import ResponseListRefactor

class MaintableRepository(ABC):
    """
    Clase Base Abstracta (ABC) que define la interfaz del repositorio
    para las operaciones de datos de las tablas de mantenimiento.
    """

    @abstractmethod
    async def get_by_table_name(
        self,
        table_name: str,
        page_index: int,
        page_size: int,
        order_by: str,
        sort_by: str,
        query: Optional[str] = None,
    ) -> ResponseListRefactor[MaintableEntity]:
        """
        Método abstracto para obtener registros de una tabla de mantenimiento
        con paginación, filtro y ordenamiento.

        Args:
            table_name: Nombre de la tabla para filtrar los registros.
            page_index: Índice de la página.
            page_size: Tamaño de la página.
            query: Término de búsqueda opcional para filtrar por item_text.
            sort_by: Campo por el cual ordenar.
            order: Dirección del ordenamiento ('asc' o 'desc').
        """
        pass