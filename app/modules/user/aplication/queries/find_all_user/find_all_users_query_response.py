from datetime import datetime

from pydantic import BaseModel

from app.modules.user.aplication.queries.find_all_role.find_all_role_query_response import (
    FindAllRoleQueryResponse,
)
from app.modules.user.domain.models.user_enum import Status


class FindAllUsersQueryResponse(BaseModel):
    id: int
    user_name: str
    email: str
    status: Status
    role: FindAllRoleQueryResponse
    created_at: datetime
