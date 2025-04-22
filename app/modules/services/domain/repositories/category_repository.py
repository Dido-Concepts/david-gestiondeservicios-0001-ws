from abc import ABC, abstractmethod
from typing import Optional

from app.modules.services.domain.entities.category_domain import CategoryEntity


class CategoryRepository(ABC):

    @abstractmethod
    async def create_category(
        self,
        name_category: str,
        user_create: str,
        description_category: Optional[str]
    ) -> int:
        pass

    @abstractmethod
    async def find_categories(self) -> list[CategoryEntity]:
        """
        Recupera una lista de todas las categorías activas desde el almacén de datos.

        Devuelve:
            Una lista que contiene objetos CategoryResponse para todas las categorías activas.
            Devuelve una lista vacía si no se encuentran categorías activas.

        Genera:
            DatabaseError: Si ocurre un problema durante la recuperación de datos.
            # Añadir otras excepciones específicas según sea necesario
        """
        pass
