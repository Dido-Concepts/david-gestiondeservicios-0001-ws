from abc import ABC, abstractmethod
from typing import Optional

# Importaciones específicas del módulo
from app.modules.maintable.domain.entities.maintable_domain import MaintableEntity
# Importación de tipo compartido
from app.modules.share.domain.repositories.repository_types import ResponseList


class MaintableRepository(ABC):
    """
    Clase Base Abstracta (ABC) que define la interfaz del repositorio
    para las operaciones de datos de maintable.
    Las implementaciones concretas interactuarán con la base de datos real.
    """

    @abstractmethod
    async def get_day_off_types(
        self, 
        table_name: str,
        page_index: int, 
        page_size: int, 
        query: Optional[str] = None,
        sort_by: str = 'maintable_id',
        order: str = 'ASC'
    ) -> ResponseList[MaintableEntity]:
        """
        Método abstracto para obtener tipos de días libres de la tabla maintable con paginación.
        Utiliza el stored procedure maintable_sp_get_by_criteria.
        
        Args:
            table_name: Nombre de la tabla para filtrar los registros
            page_index: Índice de la página (0-based)
            page_size: Tamaño de la página
            query: Término de búsqueda opcional para filtrar por item_text
            sort_by: Campo por el cual ordenar (maintable_id, item_text, item_value, item_order, insert_date)
            order: Dirección del ordenamiento (ASC o DESC)
        
        Returns:
            ResponseList[MaintableEntity]: Objeto que contiene una lista de objetos
            MaintableEntity y metadatos de paginación (total de items, total de páginas).
        """
        pass  # La implementación real estará en la subclase concreta
