import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class CreateCategoryRequest(BaseModel):
    name_category: str
    description_category: Optional[str] = None

    @field_validator("name_category")
    def validate_name_category(cls, v: str) -> str:
        """
        Valida que name_category no esté vacío, no contenga solo espacios
        y solo contenga letras (incluyendo tildes y ñ), números y espacios.
        """
        if not v or not v.strip():
            raise ValueError("name_category no puede ser vacío ni contener solo espacios.")
        # Regex para permitir letras (mayúsculas, minúsculas, con tildes), ñ, números y espacios.
        # ^                  -> inicio de la cadena
        # [A-ZÁÉÍÓÚÜÑ...]   -> conjunto de caracteres permitidos
        # +                  -> una o más ocurrencias de los caracteres permitidos
        # $                  -> fin de la cadena
        if not re.match(r"^[A-ZÁÉÍÓÚÜÑa-záéíóúüñ0-9 ]+$", v):
            raise ValueError("name_category solo debe contener letras (incluyendo tildes y ñ), números y espacios.")

        return v

    @field_validator("description_category")
    def validate_description_category(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida description_category si se proporciona un valor.
        Permite None. Si no es None, aplica las mismas reglas que name_category:
        no vacío, no solo espacios, y solo caracteres permitidos.
        """
        if v is None:
            return v

        if not v or not v.strip():
            raise ValueError("description_category, si se proporciona, no puede ser vacío ni contener solo espacios.")

        if not re.match(r"^[A-ZÁÉÍÓÚÜÑa-záéíóúüñ0-9 ]+$", v):
            raise ValueError("description_category, si se proporciona, solo debe contener letras (incluyendo tildes y ñ), números y espacios.")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name_category": "Tecnología Móvil",
                "description_category": "Smartphones tablets y accesorios 2025"
            }
        }
    )
