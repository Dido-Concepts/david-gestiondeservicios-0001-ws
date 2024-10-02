from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)
from app.modules.share.aplication.mediator.mediator import Mediator
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
)
from app.modules.user.aplication.comands.change_status_user.change_status_user_command import (
    ChangeStatusUserCommand,
)
from app.modules.user.aplication.comands.create_user.create_user_command import (
    CreateUserCommand,
)
from app.modules.user.aplication.comands.edit_user.edit_user_command import (
    EditUserCommand,
)
from app.modules.user.aplication.queries.find_all_user.find_all_users_query import (
    FindAllUsersQuery,
)
from app.modules.user.aplication.queries.find_all_user.find_all_users_query_response import (
    FindAllUsersQueryResponse,
)
from app.modules.user.presentation.dependencies.user_dependencies import (
    get_user_mediator,
)

user_router = APIRouter()


@user_router.get(
    "/user", dependencies=[Depends(permission_required("user:list_users"))]
)
async def list_users(
    query_params: Annotated[FindAllUsersQuery, Query()],
    mediator: Mediator[
        FindAllUsersQuery, PaginatedItemsViewModel[FindAllUsersQueryResponse]
    ] = Depends(get_user_mediator),
) -> PaginatedItemsViewModel[FindAllUsersQueryResponse]:
    result = await mediator.send(query_params)
    return result


@user_router.post(
    "/user", dependencies=[Depends(permission_required("user:create_user"))]
)
async def create_user(
    command: CreateUserCommand,
    mediator: Mediator[CreateUserCommand, bool] = Depends(get_user_mediator),
) -> bool:
    result = await mediator.send(command)
    return result


@user_router.put("/user", dependencies=[Depends(permission_required("user:edit_user"))])
async def edit_user(
    command: EditUserCommand,
    mediator: Mediator[EditUserCommand, bool] = Depends(get_user_mediator),
) -> bool:
    result = await mediator.send(command)
    return result


@user_router.patch(
    "/user", dependencies=[Depends(permission_required("user:change_status_user"))]
)
async def change_status_user(
    command: Annotated[ChangeStatusUserCommand, Query()],
    mediator: Mediator[ChangeStatusUserCommand, bool] = Depends(get_user_mediator),
) -> bool:
    result = await mediator.send(command)
    return result
