from pydantic import BaseModel

from app.modules.user.domain.models.user_enum import Status


class ChangeStatusUserCommand(BaseModel):
    id_user: int
    status: Status
