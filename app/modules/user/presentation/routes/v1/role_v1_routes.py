from typing import List

from fastapi import APIRouter, Depends

from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)
from app.modules.share.aplication.mediator.mediator import Mediator
from app.modules.user.aplication.queries.find_all_role.find_all_role_query import (
    FindAllRoleQuery,
)
from app.modules.user.aplication.queries.find_all_role.find_all_role_query_response import (
    FindAllRoleQueryResponse,
)
from app.modules.user.presentation.dependencies.role_dependencies import (
    get_role_mediator,
)

role_router = APIRouter()


@role_router.get(
    "/role", dependencies=[Depends(permission_required("role:list_roles"))]
)
async def list_roles(
    mediator: Mediator[FindAllRoleQuery, List[FindAllRoleQueryResponse]] = Depends(
        get_role_mediator
    )
) -> List[FindAllRoleQueryResponse]:

    result = await mediator.send(FindAllRoleQuery())
    return result
