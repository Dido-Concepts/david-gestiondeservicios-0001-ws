from fastapi import APIRouter, Depends, Query
from app.modules.user.aplication.mediator.user_mediator import UserMediator
from app.modules.user.domain.models.user_domain import User
from app.modules.user.aplication.comands.create_user.create_user_command import (
    CreateUserCommand,
)
from app.modules.user.presentation.dependencies.user_dependencies import (
    get_user_mediator,
)

from app.modules.user.aplication.queries.find_all_user.find_all_users_query import (
    FindAllUsersQuery,
)
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
)


user_router = APIRouter()


@user_router.get("/users")
async def list_users(
    page_index: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    mediator: UserMediator = Depends(get_user_mediator),
) -> PaginatedItemsViewModel[User]:
    query = FindAllUsersQuery(page_index=page_index, page_size=page_size)
    result = await mediator.send(query)
    return result


@user_router.post("/user")
async def create_user(
    command: CreateUserCommand, mediator: UserMediator = Depends(get_user_mediator)
) -> bool:
    result = await mediator.send(command)
    return result
