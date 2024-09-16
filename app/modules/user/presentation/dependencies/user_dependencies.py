from fastapi import Depends
from typing import AsyncIterator
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.database import create_session
from app.modules.user.domain.repositories.user_repository import UserRepository
from app.modules.user.infra.repositories.user_implementation_respository import (
    UserImplementationRepository,
)
from app.modules.user.aplication.comands.create_user.create_user_command import (
    CreateUserCommand,
)
from app.modules.user.aplication.comands.create_user.create_user_command_handler import (
    CreateUserCommandHandler,
)
from app.modules.user.aplication.mediator.user_mediator import UserMediator


async def get_uow() -> AsyncIterator[UnitOfWork]:
    async with UnitOfWork(session_factory=create_session) as uow:
        yield uow


async def get_user_repository(
    uow: UnitOfWork = Depends(get_uow),
) -> UserRepository:
    return UserImplementationRepository(uow)


async def get_user_mediator(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserMediator:
    mediator = UserMediator()
    mediator.register_handler(
        CreateUserCommand,
        CreateUserCommandHandler(user_repository=user_repository),
    )
    return mediator
