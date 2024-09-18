from pydantic import BaseModel
from datetime import datetime
from app.modules.user.domain.models.user_enum import Status


class RoleResponse(BaseModel):
    id: int
    description: str


class FindAllUsersQueryResponse(BaseModel):
    id: int
    user_name: str
    email: str
    status: Status
    role: RoleResponse
    created_at: datetime
