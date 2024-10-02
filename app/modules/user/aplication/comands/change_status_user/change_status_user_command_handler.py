from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.user.aplication.comands.change_status_user.change_status_user_command import (
    ChangeStatusUserCommand,
)
from app.modules.user.domain.repositories.user_repository import UserRepository


class ChangeStatusUserCommandHandler(IRequestHandler[ChangeStatusUserCommand, bool]):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def handle(self, command: ChangeStatusUserCommand) -> bool:
        await self.user_repository.change_status_user(
            id_user=command.id_user, status=command.status
        )
        return True
