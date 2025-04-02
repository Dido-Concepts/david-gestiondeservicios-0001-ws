from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class ChangeStatusLocationCommand(BaseModel):
    id_location: int
    user_updated: str


@Mediator.handler
class GetLocationByIdQueryHandler(IRequestHandler[ChangeStatusLocationCommand, str]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.location_repository = injector.get(LocationRepository)  # type: ignore[type-abstract]

    async def handle(self, command: ChangeStatusLocationCommand) -> str:
        res = await self.location_repository.change_status_location(
            location_id=command.id_location, user_update=command.user_updated
        )

        return res
