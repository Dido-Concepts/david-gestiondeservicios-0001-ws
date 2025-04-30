from abc import ABC, abstractmethod
from typing import Optional

from app.modules.services.domain.entities.category_domain import CategoryEntity


class CategoryRepository(ABC):

    @abstractmethod
    async def create_category(
        self,
        sede_id: int,
        category_name: str,
        description: Optional[str],
        user_create: str,
    ) -> str:
        pass

    @abstractmethod
    async def find_categories(self, location: int) -> list[CategoryEntity]:
        pass
