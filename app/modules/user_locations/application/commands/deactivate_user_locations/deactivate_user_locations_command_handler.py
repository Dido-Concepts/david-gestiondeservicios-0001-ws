# deactivate_user_locations_command_handler.py

from mediatr import Mediator
from pydantic import BaseModel

from app.modules.user_locations.domain.repositories.user_locations_repository import UserLocationsRepository
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.constants import injector_var


class DeactivateUserLocationCommand(BaseModel):
    user_id: int
    sede_id: int
    user_modifier: str


@Mediator.handler
class DeactivateUserLocationCommandHandler(IRequestHandler[DeactivateUserLocationCommand, str]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.user_locations_repository: UserLocationsRepository = injector.get(UserLocationsRepository) # type: ignore[type-abstract]

    async def handle(self, command: DeactivateUserLocationCommand) -> str:
        result_message = await self.user_locations_repository.deactivate_user_location(
            user_id=command.user_id,
            sede_id=command.sede_id,
            user_modifier=command.user_modifier
        )
        return result_message