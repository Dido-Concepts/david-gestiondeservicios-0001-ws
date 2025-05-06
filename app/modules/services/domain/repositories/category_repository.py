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

    @abstractmethod
    async def update_category(
        self,
        category_id: int,
        sede_id: int,
        category_name: str,
        description: Optional[str],
        user_update: str,
    ) -> str:
        pass

    @abstractmethod
    async def delete_category(self, category_id: int, user_delete: str) -> bool:
        pass
