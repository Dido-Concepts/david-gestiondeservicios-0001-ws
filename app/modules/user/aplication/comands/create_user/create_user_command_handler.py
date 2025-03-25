import re

from mediatr import Mediator
from pydantic import BaseModel, EmailStr, field_validator

from app.constants import injector_var
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.user.domain.repositories.user_repository import UserRepository


class CreateUserCommand(BaseModel):
    user_name: str
    email: EmailStr
    id_rol: int

    @field_validator("user_name")
    def validate_user_name(cls, value: str) -> str:
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", value):
            raise ValueError(
                "El nombre de usuario solo puede contener letras, espacios y tildes."
            )
        return value

    @field_validator("email")
    def validate_email_domain(cls, value: EmailStr) -> EmailStr:
        if not value.endswith("@gmail.com"):
            raise ValueError("El correo electrónico debe ser un Gmail (@gmail.com).")
        return value

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"user_name": "Juan Perez", "email": "example@gmail.com", "id_rol": 1}
            ]
        }
    }


@Mediator.handler
class CreateUserCommandHandler(IRequestHandler[CreateUserCommand, bool]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.user_repository = injector.get(UserRepository)  # type: ignore[type-abstract]

    async def handle(self, command: CreateUserCommand) -> bool:
        await self.user_repository.create_user(
            user_name=command.user_name, email=command.email, id_rol=command.id_rol
        )
        return True
