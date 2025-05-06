from abc import ABC, abstractmethod
from typing import Optional


class ServiceRepository(ABC):
    @abstractmethod
    async def create_service(
        self,
        service_name: str,
        description: Optional[str],
        category_id: int,
        price: float,
        duration: float,
        user_create: str,
    ) -> str:
        pass

    @abstractmethod
    async def update_service(
        self,
        service_id: int,
        service_name: str,
        description: Optional[str],
        category_id: int,
        price: float,
        duration: float,
        user_update: str,
    ) -> str:
        pass

    @abstractmethod
    async def delete_service(self, service_id: int, user_delete: str) -> bool:
        pass
