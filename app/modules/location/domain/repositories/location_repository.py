from abc import ABC, abstractmethod

from app.modules.location.domain.entities.location_domain import LocationResponse
from app.modules.location.domain.entities.location_request import Schedule
from app.modules.share.domain.repositories.repository_types import ResponseList


class LocationRepository(ABC):

    @abstractmethod
    async def create_Location(
        self,
        name_location: str,
        phone: str,
        address: str,
        file_url: str,
        file_name: str,
        file_content_type: str,
        file_size: int,
        schedule: list[Schedule],
        user_create: str,
    ) -> int:
        pass

    @abstractmethod
    async def find_locations(
        self, page_index: int, page_size: int
    ) -> ResponseList[LocationResponse]:
        pass
