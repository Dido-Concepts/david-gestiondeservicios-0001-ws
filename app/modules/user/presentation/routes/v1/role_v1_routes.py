from fastapi import APIRouter, Depends
from mediatr import Mediator

from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)
from app.modules.user.aplication.queries.find_all_role.find_all_role_query_handler import (
    FindAllRoleQuery,
    FindAllRoleQueryResponse,
)


class RoleController:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.get(
            "/role", dependencies=[Depends(permission_required(roles=["admin"]))]
        )(self.list_roles)

    async def list_roles(self) -> list[FindAllRoleQueryResponse]:

        result: list[FindAllRoleQueryResponse] = await self.mediator.send_async(
            FindAllRoleQuery()
        )
        return result
