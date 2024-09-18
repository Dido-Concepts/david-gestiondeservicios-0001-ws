from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
)
from app.modules.user.aplication.comands.create_user.create_user_command import (
    CreateUserCommand,
)
from app.modules.user.aplication.mediator.user_mediator import UserMediator
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


@user_router.get("/users")
async def list_users(
    query_params: Annotated[FindAllUsersQuery, Query()],
    mediator: UserMediator[
        FindAllUsersQuery, PaginatedItemsViewModel[FindAllUsersQueryResponse]
    ] = Depends(get_user_mediator),
) -> PaginatedItemsViewModel[FindAllUsersQueryResponse]:
    result = await mediator.send(query_params)
    return result


@user_router.post("/user")
async def create_user(
    command: CreateUserCommand,
    mediator: UserMediator[CreateUserCommand, bool] = Depends(get_user_mediator),
) -> bool:
    result = await mediator.send(command)
    return result
