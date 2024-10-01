from abc import ABC, abstractmethod
from typing import List

from app.modules.user.domain.models.role_domain import Role, RolePermission


class RoleRepository(ABC):

    @abstractmethod
    async def find_permissions_by_role_id(self, role_id: int) -> List[RolePermission]:
        pass

    @abstractmethod
    async def find_all(self) -> List[Role]:
        pass
