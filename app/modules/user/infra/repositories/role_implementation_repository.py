from typing import List

from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.user.domain.models.role_domain import Role, RolePermission
from app.modules.user.domain.repositories.role_repository import RoleRepository
from app.modules.user.infra.mappers.role_mapper import RoleMapper
from app.modules.user.infra.mappers.role_permission_mapper import RolePermissionMapper
from app.modules.user.infra.migration.models import Permissions, Roles


class RoleImplementationRepository(RoleRepository):
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        self._role_permission_mapper = RolePermissionMapper()
        self._role_mapper = RoleMapper()

    async def find_permissions_by_role_id(self, role_id: int) -> List[RolePermission]:
        async with self._uow as uow:
            session = uow.session

            smt = (
                select(Permissions)
                .options(
                    joinedload(Permissions.role),
                    joinedload(Permissions.accion),
                )
                .where(Permissions.role_id == role_id)
            )

            result = await session.execute(smt)
            roles_permissions = result.scalars().all()

            permissions = [
                self._role_permission_mapper.map_from(role_permission)
                for role_permission in roles_permissions
            ]

            return permissions

    async def find_all(self) -> List[Role]:
        async with self._uow as uow:
            session = uow.session

            result = await session.execute(select(Roles))
            roles = result.scalars().all()

            return [self._role_mapper.map_from(role) for role in roles]
