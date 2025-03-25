from typing import Optional

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.user.domain.repositories.role_repository import RoleRepository
from app.modules.user.domain.repositories.user_repository import UserRepository


class FindRolPermissionQuery(BaseModel):
    email: str


class FindRolPermissionQueryResponse(BaseModel):
    role: Optional[str] = None
    permissions: Optional[list[str]] = None


@Mediator.handler
class FindRolPermissionQueryHandler(
    IRequestHandler[FindRolPermissionQuery, FindRolPermissionQueryResponse]
):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.user_repository = injector.get(UserRepository)  # type: ignore[type-abstract]
        self.role_repository = injector.get(RoleRepository)  # type: ignore[type-abstract]

    async def handle(
        self, query: FindRolPermissionQuery
    ) -> FindRolPermissionQueryResponse:

        user = await self.user_repository.find_user_by_email(email=query.email)

        permissions_res = await self.role_repository.find_permissions_by_role_id(
            role_id=user.role.id
        )
        permissions = [permission.action.name for permission in permissions_res]

        return FindRolPermissionQueryResponse(
            role=user.role.name,
            permissions=permissions,
        )
