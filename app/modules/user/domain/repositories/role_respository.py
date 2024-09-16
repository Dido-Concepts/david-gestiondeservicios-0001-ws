from abc import ABC, abstractmethod

from app.modules.user.domain.models.role_domain import Role


class RoleRepository(ABC):
    @abstractmethod
    def get_role_by_id(self, role_id: int) -> Role:
        pass
