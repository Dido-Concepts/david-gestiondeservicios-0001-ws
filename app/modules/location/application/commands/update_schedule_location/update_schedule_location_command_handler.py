from mediatr import Mediator
from pydantic import BaseModel

from app.modules.location.application.request.create_location_request import ScheduleRequest
from app.modules.location.domain.entities.location_domain import ScheduleRangeDomain, ScheduleRequestDomain
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.constants import injector_var
from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)
from app.modules.share.utils.json_to_objects import json_to_objects


class UpdateScheduleLocationCommand(BaseModel):
    location_id: int
    schedule: str
    user_modify: str


@Mediator.handler
class UpdateScheduleLocationCommandHandler(IRequestHandler[UpdateScheduleLocationCommand, str]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.location_repository = injector.get(LocationRepository)  # type: ignore[type-abstract]

    async def handle(self, command: UpdateScheduleLocationCommand) -> str:

        schedule_list = json_to_objects(
            json_string=command.schedule, cls=ScheduleRequest
        )

        schedule_list_request = [
            ScheduleRequestDomain(
                day=s.day,
                ranges=[
                    ScheduleRangeDomain(start=r.start, end=r.end) for r in s.ranges
                ],
            )
            for s in schedule_list
        ]

        result = await self.location_repository.update_schedule_location(
            location_id=command.location_id,
            schedule=schedule_list_request,
            user_modify=command.user_modify,
        )

        return result
