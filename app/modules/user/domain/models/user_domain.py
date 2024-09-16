from dataclasses import dataclass
from typing import Optional
from app.modules.user.domain.models.role_domain import Role


@dataclass
class User:
    id: Optional[int]
    user_name: str
    email: str
    role: Role
