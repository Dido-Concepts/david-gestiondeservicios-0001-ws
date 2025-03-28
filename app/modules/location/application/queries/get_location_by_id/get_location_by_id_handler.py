from datetime import datetime

from mediatr import Mediator
from pydantic import BaseModel, Field

from app.constants import injector_var
from app.modules.location.domain.entities.location_domain import DayOfWeek
from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)
from app.modules.share.domain.file.file_domain import FileResponse
from app.modules.share.domain.handler.request_handler import IRequestHandler


class GetLocationByIdQuery(BaseModel):
    id_location: int = Field(1, ge=1)


class ScheduleRange(BaseModel):
    start: str
    end: str


class ScheduleResponse(BaseModel):
    day: DayOfWeek
    ranges: list[ScheduleRange]


class GetLocationByIdResponse(BaseModel):
    id: int
    name_location: str
    phone_location: str
    address_location: str
    insert_date: datetime
    file: FileResponse
    location_review: str
    schedules: list[ScheduleResponse]


@Mediator.handler
class GetLocationByIdQueryHandler(
    IRequestHandler[GetLocationByIdQuery, GetLocationByIdResponse]
):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.location_repository = injector.get(LocationRepository)  # type: ignore[type-abstract]

    async def handle(self, query: GetLocationByIdQuery) -> GetLocationByIdResponse:

        res = await self.location_repository.find_location_by_id(
            location_id=query.id_location
        )

        location_response = GetLocationByIdResponse(
            id=res.id,
            name_location=res.nombre_sede,
            phone_location=res.telefono_sede,
            address_location=res.direccion_sede,
            insert_date=res.insert_date,
            location_review=res.location_review,
            file=res.file,
            schedules=[
                ScheduleResponse(
                    day=DayOfWeek(s.day),
                    ranges=[ScheduleRange(start=r.start, end=r.end) for r in s.ranges],
                )
                for s in res.schedules
            ],
        )

        return location_response
