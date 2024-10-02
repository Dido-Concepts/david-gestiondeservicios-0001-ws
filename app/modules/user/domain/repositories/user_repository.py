from abc import ABC, abstractmethod

from app.modules.share.domain.repositories.repository_types import ResponseList
from app.modules.user.domain.models.user_domain import UserRole
from app.modules.user.domain.models.user_enum import Status


class UserRepository(ABC):
    @abstractmethod
    async def create_user(self, user_name: str, email: str, id_rol: int) -> bool:
        pass

    @abstractmethod
    async def find_users(
        self, page_index: int, page_size: int
    ) -> ResponseList[UserRole]:
        pass

    @abstractmethod
    async def edit_user(self, user_name: str, id_rol: int, id_user: int) -> bool:
        pass

    @abstractmethod
    async def change_status_user(self, id_user: int, status: Status) -> bool:
        pass

    @abstractmethod
    async def find_user_by_email(self, email: str) -> UserRole:
        pass
