from datetime import datetime, date
from typing import Optional

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.user_locations.domain.repositories.user_locations_repository import (
    UserLocationsRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class GetUserByLocationQuery(BaseModel):
    sede_id: int
    start_date: date
    end_date: date


class GetUserByLocationQueryResponse(BaseModel):
    user_id: int
    user_name: str
    email: str
    event_type: Optional[str] = None
    event_id: Optional[int] = None
    event_start_time: Optional[datetime] = None
    event_end_time: Optional[datetime] = None
    event_description: Optional[str] = None
    event_sede_id: Optional[int] = None


@Mediator.handler
class GetUserByLocationQueryHandler(
    IRequestHandler[
        GetUserByLocationQuery, list[GetUserByLocationQueryResponse]
    ]
):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.user_locations_repository = injector.get(UserLocationsRepository)  # type: ignore[type-abstract]

    async def handle(
        self, query: GetUserByLocationQuery
    ) -> list[GetUserByLocationQueryResponse]:
        res = await self.user_locations_repository.get_user_by_location(
            sede_id=query.sede_id,
            start_date=query.start_date,
            end_date=query.end_date
        )

        response_data = [
            GetUserByLocationQueryResponse(
                user_id=user_event.user_id,
                user_name=user_event.user_name,
                email=user_event.email,
                event_type=user_event.event_type,
                event_id=user_event.event_id,
                event_start_time=user_event.event_start_time,
                event_end_time=user_event.event_end_time,
                event_description=user_event.event_description,
                event_sede_id=user_event.event_sede_id,
            )
            for user_event in res
        ]
        return response_data 