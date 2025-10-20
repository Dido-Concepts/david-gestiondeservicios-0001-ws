from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SendWhatsappMessageRequest(BaseModel):
    """
    Modelo Pydantic para la solicitud de envío de mensaje de WhatsApp vía API.
    Define la estructura esperada y aplica validaciones a los datos de entrada.
    """

    # --- Campos del Modelo ---
    number: str = Field(
        ...,
        description="Número de WhatsApp para recibir el mensaje (con código de país)",
        min_length=10,
        max_length=20,
    )
    text: str = Field(
        ..., description="Texto del mensaje a enviar", min_length=1, max_length=4096
    )
    delay: Optional[int] = Field(
        default=None,
        description="Tiempo de presencia en milisegundos antes de enviar el mensaje",
        ge=0,
    )
    linkPreview: Optional[bool] = Field(
        default=True,
        description="Muestra una vista previa del sitio web de destino si hay un enlace dentro del mensaje",
    )

    # --- Validadores de Campo ---
    @field_validator("number")
    def validate_number_format(cls, v: str) -> str:
        """
        Valida el formato del número de WhatsApp.
        Debe contener solo dígitos y tener entre 10 y 20 caracteres.
        """
        # Remover espacios y caracteres especiales comunes
        cleaned_number = "".join(filter(str.isdigit, v))

        if len(cleaned_number) < 10 or len(cleaned_number) > 20:
            raise ValueError("El número debe tener entre 10 y 20 dígitos")

        return cleaned_number

    @field_validator("text")
    def validate_text_content(cls, v: str) -> str:
        """
        Valida que el texto no esté vacío después de remover espacios en blanco.
        """
        if not v.strip():
            raise ValueError("El texto del mensaje no puede estar vacío")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "number": "5531912345678",
                "text": "¡Hola! Este es un mensaje de prueba desde la API.",
                "delay": 1000,
                "linkPreview": True,
            }
        },
        validate_assignment=True,
        extra="forbid",
    )
