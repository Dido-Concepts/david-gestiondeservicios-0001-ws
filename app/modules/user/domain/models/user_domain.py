from dataclasses import dataclass
from datetime import datetime
from app.modules.user.domain.models.role_domain import Role, Rol
from app.modules.user.domain.models.user_enum import Status


@dataclass
class UserWithRoleAndPermissions:
    id: int
    user_name: str
    email: str
    role: Role


@dataclass
class User:
    id: int
    user_name: str
    email: str
    status: Status
    rol: Rol
    created_at: datetime
