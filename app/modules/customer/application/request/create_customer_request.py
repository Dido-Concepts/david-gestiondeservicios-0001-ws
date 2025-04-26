from enum import Enum
import re  # Para usar expresiones regulares en las validaciones
from typing import Optional
from datetime import date

# Importaciones de Pydantic para validación de modelos y campos
from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr


class CustomerStatusEnum(str, Enum):
    """Enumera los estados válidos para un cliente."""
    ACTIVE = 'active'
    BLOCKED = 'blocked'


class CreateCustomerRequest(BaseModel):
    """
    Modelo Pydantic para la solicitud de creación de un cliente vía API.
    Define la estructura esperada y aplica validaciones a los datos de entrada.
    """
    # --- Campos del Modelo ---
    name_customer: str = Field(..., description="Nombre completo del cliente.")
    # EmailStr ya valida el formato del correo electrónico. Optional permite que sea None.
    email_customer: Optional[EmailStr] = Field(None, description="Correo electrónico del cliente.")
    phone_customer: Optional[str] = Field(None, description="Número de teléfono del cliente (formato libre).")
    # Pydantic valida automáticamente si la cadena se puede convertir a un objeto date (formato YYYY-MM-DD).
    # Optional permite que sea None.
    birthdate_customer: Optional[date] = Field(None, description="Fecha de nacimiento del cliente (YYYY-MM-DD).")
    # Usamos el Enum definido para restringir los valores. Optional permite que sea None.
    status_customer: Optional[CustomerStatusEnum] = Field(CustomerStatusEnum.ACTIVE, description="Estado actual del cliente.")

    # --- Validadores de Campo ---

    @field_validator("name_customer")
    def validate_name_customer(cls, v: str) -> str:
        """
        Valida que name_customer no esté vacío, no contenga solo espacios
        y solo contenga letras (incluyendo tildes y ñ) y espacios.
        No permite números ni caracteres especiales excepto espacios.
        """
        if not v or not v.strip():
            raise ValueError("name_customer no puede ser vacío ni contener solo espacios.")

        # Regex para permitir solo letras (mayúsculas, minúsculas, con tildes), ñ y espacios.
        # ^                  -> inicio de la cadena
        # [A-ZÁÉÍÓÚÜÑa-z... ] -> conjunto de caracteres permitidos (letras con acentos, ñ, espacio)
        # +                  -> una o más ocurrencias
        # $                  -> fin de la cadena
        # Se eliminaron los números 0-9 del regex de tu ejemplo.
        # Se pueden añadir otros caracteres comunes en nombres si es necesario (ej: guión '-', apóstrofe ''')
        # Ejemplo con guión y apóstrofe: r"^[A-ZÁÉÍÓÚÜÑa-záéíóúüñ' -]+$"
        if not re.match(r"^[A-ZÁÉÍÓÚÜÑa-záéíóúüñ ]+$", v.strip()):
            raise ValueError("name_customer solo debe contener letras (incluyendo tildes y ñ) y espacios.")

        # Devolvemos el valor sin espacios al inicio/final para consistencia
        return v.strip()

    @field_validator("phone_customer")
    def validate_phone(cls, v: str) -> str:
        if not v.isdigit() or not v.startswith("9") or len(v) != 9:
            raise ValueError(
                "phone debe ser un número de 9 dígitos que comience con '9'"
            )
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name_customer": "Ana María López García",
                "email_customer": "ana.lopez@email.provider.com",
                "phone_customer": "999888777",
                "birthdate_customer": "1992-04-15",
                "status_customer": CustomerStatusEnum.ACTIVE.value
            }
        },
        # Configuración adicional útil:
        validate_assignment=True,
        extra='forbid'
    )
