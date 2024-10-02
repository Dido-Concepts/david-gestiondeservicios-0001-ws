from typing import Any

from fastapi import Depends

from app.modules.share.aplication.mediator.mediator import Mediator
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.infra.persistence.unit_of_work_instance import get_uow
from app.modules.user.aplication.queries.find_all_role.find_all_role_query import (
    FindAllRoleQuery,
)
from app.modules.user.aplication.queries.find_all_role.find_all_role_query_handler import (
    FindAllRoleHandler,
)
from app.modules.user.domain.repositories.role_repository import RoleRepository
from app.modules.user.infra.repositories.role_implementation_repository import (
    RoleImplementationRepository,
)


async def get_role_repository(
    uow: UnitOfWork = Depends(get_uow),
) -> RoleRepository:
    return RoleImplementationRepository(uow)


async def get_role_mediator(
    role_repository: RoleRepository = Depends(get_role_repository),
) -> Mediator[Any, Any]:
    mediator: Mediator[Any, Any] = Mediator()

    mediator.register_handler(
        FindAllRoleQuery,
        FindAllRoleHandler(role_repository=role_repository),
    )

    return mediator
