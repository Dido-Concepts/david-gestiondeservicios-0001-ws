from abc import ABC, abstractmethod

from app.modules.location.domain.entities.location_request import Schedule


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
