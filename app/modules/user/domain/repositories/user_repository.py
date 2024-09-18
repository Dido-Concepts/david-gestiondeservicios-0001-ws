from abc import ABC, abstractmethod

from app.modules.share.domain.repositories.repository_types import ResponseList
from app.modules.user.domain.models.user_domain import UserRole


class UserRepository(ABC):
    @abstractmethod
    async def create_user(self, user_name: str, email: str, id_rol: int) -> bool:
        pass

    @abstractmethod
    async def find_all_users(
        self, page_index: int, page_size: int
    ) -> ResponseList[UserRole]:
        pass
