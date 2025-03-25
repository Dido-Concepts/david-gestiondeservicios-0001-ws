from fastapi import APIRouter, Depends
from mediatr import Mediator

from app.modules.auth.application.queries.find_rol_permission.find_rol_permission_query_handler import (
    FindRolPermissionQuery,
    FindRolPermissionQueryResponse,
)
from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_current_user,
)


class AuthController:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.get("/get-user-info")(self.get_user_info)

    async def get_user_info(
        self,
        user_info: UserAuth = Depends(get_current_user),
    ) -> FindRolPermissionQueryResponse:

        if not user_info.email:
            raise ValueError("User email not found in token")

        result: FindRolPermissionQueryResponse = await self.mediator.send_async(
            FindRolPermissionQuery(email=user_info.email)
        )

        return result
