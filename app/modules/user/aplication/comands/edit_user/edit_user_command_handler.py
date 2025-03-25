import re

from mediatr import Mediator
from pydantic import BaseModel, field_validator

from app.constants import injector_var
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.user.domain.repositories.user_repository import UserRepository


class EditUserCommand(BaseModel):
    user_name: str
    id_rol: int
    id_user: int

    @field_validator("user_name")
    def validate_user_name(cls, value: str) -> str:
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", value):
            raise ValueError(
                "El nombre de usuario solo puede contener letras, espacios y tildes."
            )
        return value

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_name": "Juan Perez",
                    "id_rol": 1,
                    "id_user": 1,
                }
            ]
        }
    }


@Mediator.handler
class EditUserCommandHandler(IRequestHandler[EditUserCommand, bool]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.user_repository = injector.get(UserRepository)  # type: ignore[type-abstract]

    async def handle(self, command: EditUserCommand) -> bool:
        await self.user_repository.edit_user(
            user_name=command.user_name,
            id_rol=command.id_rol,
            id_user=command.id_user,
        )
        return True
