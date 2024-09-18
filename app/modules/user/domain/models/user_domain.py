from dataclasses import dataclass
from datetime import datetime
from app.modules.user.domain.models.user_enum import Status
from app.modules.user.domain.models.role_domain import Role


@dataclass
class User:
    id: int
    user_name: str
    email: str
    status: Status
    created_at: datetime


@dataclass
class UserRole:
    id: int
    user: User
    role: Role
