from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.user.aplication.comands.edit_user.edit_user_command import (
    EditUserCommand,
)
from app.modules.user.domain.repositories.user_repository import UserRepository


class EditUserCommandHandler(IRequestHandler[EditUserCommand, bool]):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def handle(self, command: EditUserCommand) -> bool:
        await self.user_repository.edit_user(
            user_name=command.user_name,
            id_rol=command.id_rol,
            id_user=command.id_user,
        )
        return True
