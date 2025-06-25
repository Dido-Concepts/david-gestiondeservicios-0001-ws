from abc import ABC, abstractmethod
from typing import Optional

from app.modules.location.domain.entities.location_domain import (
    LocationEntity,
    LocationInfoResponse,
    LocationResponse,
    ScheduleRequestDomain,
    SedeDomain,
)
from app.modules.share.domain.repositories.repository_types import (
    ResponseList,
    ResponseListRefactor,
)


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
        schedule: list[ScheduleRequestDomain],
        user_create: str,
        location_review: Optional[str] = None,
    ) -> int:
        pass

    @abstractmethod
    async def find_locations(
        self, page_index: int, page_size: int
    ) -> ResponseList[LocationResponse]:
        pass

    @abstractmethod
    async def find_location_refactor(
        self,
        page_index: int,
        page_size: int,
        order_by: str,
        sort_by: str,
        query: Optional[str] = None,
    ) -> ResponseListRefactor[LocationEntity]:
        pass

    @abstractmethod
    async def find_location_by_id(self, location_id: int) -> LocationInfoResponse:
        pass

    @abstractmethod
    async def change_status_location(self, location_id: int, user_update: str) -> str:
        pass

    @abstractmethod
    async def update_details_location(
        self,
        location_id: int,
        name: str,
        phone: str,
        address: str,
        user_modify: str,
        review_location: str,
        new_file_url: Optional[str] = None,
        new_file_filename: Optional[str] = None,
        new_file_content_type: Optional[str] = None,
        new_file_size: Optional[int] = None,
    ) -> str:
        pass

    @abstractmethod
    async def update_schedule_location(
        self,
        location_id: int,
        schedule: list[ScheduleRequestDomain],
        user_modify: str,
    ) -> str:
        pass

    @abstractmethod
    async def get_all_location_catalog(
        self,
    ) -> list[SedeDomain]:
        pass
