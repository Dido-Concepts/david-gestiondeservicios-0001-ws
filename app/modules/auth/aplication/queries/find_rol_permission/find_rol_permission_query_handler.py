from app.modules.auth.aplication.queries.find_rol_permission.find_rol_permission_query import (
    FindRolPermissionQuery,
)
from app.modules.auth.aplication.queries.find_rol_permission.find_rol_permission_query_response import (
    FindRolPermissionQueryResponse,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.user.domain.repositories.role_repository import RoleRepository
from app.modules.user.domain.repositories.user_repository import UserRepository


class FindRolPermissionQueryHandler(
    IRequestHandler[FindRolPermissionQuery, FindRolPermissionQueryResponse]
):
    def __init__(
        self, user_repository: UserRepository, role_repository: RoleRepository
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository

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
