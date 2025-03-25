import re
from datetime import datetime

from pydantic import BaseModel, ValidationInfo, field_validator

from app.modules.location.domain.entities.location_domain import DayOfWeek


class ScheduleRequest(BaseModel):
    day: DayOfWeek
    start_time: str
    end_time: str

    @field_validator("start_time", "end_time")
    def check_time_format(cls, v: str, info: ValidationInfo) -> str:
        """Valida que el formato sea HH:MM."""
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Formato de tiempo inválido, se espera HH:MM")
        return v

    @field_validator("end_time")
    def check_end_after_start(cls, v: str, info: ValidationInfo) -> str:
        """Valida que end_time sea posterior a start_time."""
        start_time = info.data.get("start_time")
        if start_time and v <= start_time:
            raise ValueError("end_time debe ser posterior a start_time")
        return v


class CreateLocationRequest(BaseModel):
    name_location: str
    phone: str
    address: str
    schedule: list[ScheduleRequest]

    @field_validator("name_location")
    def validate_name_location(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z0-9 ]+$", v):
            raise ValueError("name_location no debe contener caracteres especiales")
        return v

    @field_validator("phone")
    def validate_phone(cls, v: str) -> str:
        if not v.isdigit() or not v.startswith("9") or len(v) != 9:
            raise ValueError(
                "phone debe ser un número de 9 dígitos que comience con '9'"
            )
        return v

    @field_validator("address")
    def validate_address(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z0-9 .#]+$", v):
            raise ValueError(
                "address solo debe contener letras, números, espacios, '.', o '#'"
            )
        return v
