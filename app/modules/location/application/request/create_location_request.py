import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ValidationInfo, field_validator

from app.modules.location.domain.entities.location_domain import DayOfWeek


class ScheduleRange(BaseModel):
    start: str
    end: str

    @field_validator("start", "end")
    def check_time_format(cls, v: str) -> str:
        """Valida que el formato sea HH:MM."""
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Formato de tiempo inválido, se espera HH:MM")
        return v

    @field_validator("end")
    def check_end_after_start(cls, v: str, info: ValidationInfo) -> str:
        """Valida que fin sea posterior a inicio."""
        inicio = info.data.get("start")
        if inicio and v <= inicio:
            raise ValueError("end debe ser posterior a start")
        return v


class ScheduleRequest(BaseModel):
    day: DayOfWeek
    ranges: list[ScheduleRange]


class CreateLocationRequest(BaseModel):
    name_location: str
    phone: str
    address: str
    location_review: Optional[str] = None
    schedule: list[ScheduleRequest]

    @field_validator("name_location")
    def validate_name_location(cls, v: str) -> str:
        if not re.match(r"^[A-ZÁÉÍÓÚÜÑáéíóúüña-z0-9 ]+$", v):
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
        if not re.match(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 .#]+$", v):
            raise ValueError(
                "address solo debe contener letras, números, espacios, '.', o '#'"
            )
        return v

    @field_validator("location_review")
    def validate_location_review(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 .,#]+$", v):
            raise ValueError(
                "location_review solo debe contener letras, números, espacios, ',', '#' o '.'"
            )
        return v
