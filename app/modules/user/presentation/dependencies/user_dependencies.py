from typing import Any

from fastapi import Depends

from app.modules.share.aplication.mediator.mediator import Mediator
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.infra.persistence.unit_of_work_instance import get_uow
from app.modules.user.aplication.comands.change_status_user.change_status_user_command import (
    ChangeStatusUserCommand,
)
from app.modules.user.aplication.comands.change_status_user.change_status_user_command_handler import (
    ChangeStatusUserCommandHandler,
)
from app.modules.user.aplication.comands.create_user.create_user_command import (
    CreateUserCommand,
)
from app.modules.user.aplication.comands.create_user.create_user_command_handler import (
    CreateUserCommandHandler,
)
from app.modules.user.aplication.comands.edit_user.edit_user_command import (
    EditUserCommand,
)
from app.modules.user.aplication.comands.edit_user.edit_user_command_handler import (
    EditUserCommandHandler,
)
from app.modules.user.aplication.queries.find_all_user.find_all_users_query import (
    FindAllUsersQuery,
)
from app.modules.user.aplication.queries.find_all_user.find_all_users_query_handler import (
    FindAllUsersQueryHandler,
)
from app.modules.user.domain.repositories.user_repository import UserRepository
from app.modules.user.infra.repositories.user_implementation_repository import (
    UserImplementationRepository,
)


async def get_user_repository(
    uow: UnitOfWork = Depends(get_uow),
) -> UserRepository:
    return UserImplementationRepository(uow)


async def get_user_mediator(
    user_repository: UserRepository = Depends(get_user_repository),
) -> Mediator[Any, Any]:
    mediator: Mediator[Any, Any] = Mediator()

    mediator.register_handler(
        CreateUserCommand,
        CreateUserCommandHandler(user_repository=user_repository),
    )
    mediator.register_handler(
        FindAllUsersQuery,
        FindAllUsersQueryHandler(user_repository=user_repository),
    )
    mediator.register_handler(
        EditUserCommand,
        EditUserCommandHandler(user_repository=user_repository),
    )
    mediator.register_handler(
        ChangeStatusUserCommand,
        ChangeStatusUserCommandHandler(user_repository=user_repository),
    )

    return mediator
