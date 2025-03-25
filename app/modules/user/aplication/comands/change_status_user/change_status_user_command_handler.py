from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.user.domain.models.user_enum import Status
from app.modules.user.domain.repositories.user_repository import UserRepository


class ChangeStatusUserCommand(BaseModel):
    id_user: int
    status: Status


@Mediator.handler
class ChangeStatusUserCommandHandler(IRequestHandler[ChangeStatusUserCommand, bool]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.user_repository = injector.get(UserRepository)  # type: ignore[type-abstract]

    async def handle(self, command: ChangeStatusUserCommand) -> bool:
        await self.user_repository.change_status_user(
            id_user=command.id_user, status=command.status
        )
        return True
