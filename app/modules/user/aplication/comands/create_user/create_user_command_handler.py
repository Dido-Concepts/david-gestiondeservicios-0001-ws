from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.user.aplication.comands.create_user.create_user_command import (
    CreateUserCommand,
)
from app.modules.user.domain.repositories.user_repository import UserRepository


class CreateUserCommandHandler(IRequestHandler[CreateUserCommand, bool]):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def handle(self, command: CreateUserCommand) -> bool:
        await self.user_repository.create_user(
            user_name=command.user_name, email=command.email, id_rol=command.id_rol
        )
        return True
