import re

from pydantic import BaseModel, field_validator


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
