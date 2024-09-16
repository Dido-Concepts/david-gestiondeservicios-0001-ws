# from app.modules.user.domain.models.user_domain import User

from abc import ABC, abstractmethod


class UserRepository(ABC):
    @abstractmethod
    async def create_user(self, user_name: str, email: str, id_rol: int) -> bool:
        pass
