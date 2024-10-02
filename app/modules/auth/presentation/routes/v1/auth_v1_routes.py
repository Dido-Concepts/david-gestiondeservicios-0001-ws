from fastapi import APIRouter, Depends

from app.modules.auth.aplication.queries.find_rol_permission.find_rol_permission_query import (
    FindRolPermissionQuery,
)
from app.modules.auth.aplication.queries.find_rol_permission.find_rol_permission_query_response import (
    FindRolPermissionQueryResponse,
)
from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_auth_mediator,
    get_current_user,
)
from app.modules.share.aplication.mediator.mediator import Mediator

auth_router = APIRouter()


@auth_router.get("/get-user-info")
async def get_user_info(
    user_info: UserAuth = Depends(get_current_user),
    mediator: Mediator[
        FindRolPermissionQuery, FindRolPermissionQueryResponse
    ] = Depends(get_auth_mediator),
) -> FindRolPermissionQueryResponse:

    if not user_info.email:
        raise ValueError("User email not found in token")

    result = await mediator.send(request=FindRolPermissionQuery(email=user_info.email))

    return result
