from aiocache import caches

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
        self.cache = caches.get("default")

    async def handle(
        self, query: FindRolPermissionQuery
    ) -> FindRolPermissionQueryResponse:

        cached_permissions = await self.cache.get(f"permissions:{query.email}")

        if cached_permissions:
            return FindRolPermissionQueryResponse(
                role=query.email, permissions=cached_permissions
            )

        res = await self.user_repository.find_user_by_email(email=query.email)

        permissions_res = await self.role_repository.find_permissions_by_role_id(
            role_id=res.role.id
        )

        permissions = [permission.action.name for permission in permissions_res]

        await self.cache.set(f"permissions:{query.email}", permissions, ttl=600)

        return FindRolPermissionQueryResponse(
            role=res.role.name,
            permissions=permissions,
        )
