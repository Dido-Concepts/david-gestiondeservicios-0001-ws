from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class CreateAppointmentRequest(BaseModel):
    """
    Modelo Pydantic para la solicitud de creación de una cita vía API.
    Define la estructura esperada y aplica validaciones a los datos de entrada.
    """

    # --- Campos del Modelo ---
    location_id: int = Field(
        ..., description="ID de la ubicación donde se realizará la cita", gt=0
    )
    user_id: int = Field(..., description="ID del empleado asignado a la cita", gt=0)
    service_id: int = Field(..., description="ID del servicio a realizar", gt=0)
    customer_id: int = Field(
        ..., description="ID del cliente que solicita la cita", gt=0
    )
    status_maintable_id: int = Field(
        ..., description="ID del estado inicial de la cita", gt=0
    )
    start_datetime: datetime = Field(
        ..., description="Fecha y hora de inicio de la cita"
    )
    end_datetime: datetime = Field(..., description="Fecha y hora de fin de la cita")

    # --- Validadores de Campo ---

    @field_validator("end_datetime")
    def validate_datetime_range(cls, v: datetime, info: ValidationInfo) -> datetime:
        """
        Valida que end_datetime sea posterior a start_datetime.
        """
        start_datetime = info.data.get("start_datetime")
        if start_datetime and v <= start_datetime:
            raise ValueError("end_datetime debe ser posterior a start_datetime")
        return v

    @field_validator("start_datetime")
    def validate_start_datetime_future(cls, v: datetime) -> datetime:
        """
        Valida que start_datetime sea en el futuro.
        """
        if v <= datetime.now():
            raise ValueError("start_datetime debe ser una fecha y hora futura")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "location_id": 1,
                "user_id": 25,
                "service_id": 3,
                "customer_id": 15,
                "status_maintable_id": 1,
                "start_datetime": "2025-12-25T10:00:00",
                "end_datetime": "2025-12-25T11:30:00",
            }
        },
        validate_assignment=True,
        extra="forbid",
    )
