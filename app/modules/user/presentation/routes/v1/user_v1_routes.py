from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from mediatr import Mediator

from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
)
from app.modules.user.aplication.comands.change_status_user.change_status_user_command_handler import (
    ChangeStatusUserCommand,
)
from app.modules.user.aplication.comands.create_user.create_user_command_handler import (
    CreateUserCommand,
)
from app.modules.user.aplication.comands.edit_user.edit_user_command_handler import (
    EditUserCommand,
)
from app.modules.user.aplication.queries.find_all_user.find_all_users_query_handler import (
    FindAllUsersQuery,
    FindAllUsersQueryResponse,
    FindAllUsersRequest,
)


class UserController:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.get(
            "/user",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.list_users)

        self.router.post(
            "/user",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.create_user)

        self.router.put(
            "/user",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.edit_user)

        self.router.patch(
            "/user",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.edit_user)

    async def list_users(
        self, query_params: Annotated[FindAllUsersRequest, Query()]
    ) -> PaginatedItemsViewModel[FindAllUsersQueryResponse]:
        try:
            query = FindAllUsersQuery(query_params)
            result: PaginatedItemsViewModel[FindAllUsersQueryResponse] = (
                await self.mediator.send_async(query)
            )
            return result
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def create_user(
        self,
        command: CreateUserCommand,
    ) -> bool:
        result: bool = await self.mediator.send_async(command)
        return result

    async def edit_user(
        self,
        command: EditUserCommand,
    ) -> bool:
        result: bool = await self.mediator.send_async(command)
        return result

    async def change_status_user(
        self,
        command: Annotated[ChangeStatusUserCommand, Query()],
    ) -> bool:
        result: bool = await self.mediator.send_async(command)
        return result
