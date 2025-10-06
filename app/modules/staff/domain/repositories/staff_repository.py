from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# Importación de tipo compartido
from app.modules.share.domain.repositories.repository_types import ResponseListRefactor

# Importaciones específicas del módulo
from app.modules.staff.domain.entities.staff_domain import StaffEntity


class StaffRepository(ABC):
    """
    Clase Base Abstracta (ABC) que define la interfaz del repositorio
    para las operaciones de datos de staff.
    Las implementaciones concretas interactuarán con la base de datos real.
    """

    @abstractmethod
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
        Método abstracto para buscar staff con paginación refactorizada.
        Utiliza el stored procedure 'staff_get_all' para obtener los datos.

        Args:
            page_index: Índice de la página.
            page_size: Tamaño de la página.
            order_by: Campo por el cual ordenar (id, user_name, email, created_at).
            sort_by: Dirección del ordenamiento ('ASC' o 'DESC').
            query: Término de búsqueda opcional para filtrar por user_name o email.
            filters: Diccionario opcional con filtros aplicables (ej: {"role_id": 7, "location_id": 4}).

        Returns:
            ResponseListRefactor[StaffEntity]: Lista paginada de miembros del staff.
        """
        pass
