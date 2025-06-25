from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from app.modules.share.domain.repositories.repository_types import ResponseListRefactor
from app.modules.services.domain.entities.service_domain import ServiceEntity2


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

    @abstractmethod
    async def find_services_by_location_v2(
        self,
        location_id: int,
        page_index: int,
        page_size: int,
        order_by: str,
        sort_by: str,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> ResponseListRefactor[ServiceEntity2]:
        pass
