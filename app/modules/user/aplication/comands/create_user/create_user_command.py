from pydantic import BaseModel, EmailStr, validator
import re


class CreateUserCommand(BaseModel):
    user_name: str
    email: EmailStr
    id_rol: int

    @validator("user_name")
    def validate_user_name(cls, value: str) -> str:
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", value):
            raise ValueError(
                "El nombre de usuario solo puede contener letras, espacios y tildes."
            )
        return value

    @validator("email")
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
