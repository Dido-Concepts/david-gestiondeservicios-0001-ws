from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator


class SendAppointmentNotificationsRequest(BaseModel):
    """
    Modelo de request para enviar notificaciones de citas por WhatsApp.
    """

    start_date: datetime = Field(
        description="Fecha y hora de inicio del rango de búsqueda (formato: YYYY-MM-DD HH:MM:SS)"
    )

    end_date: datetime = Field(
        description="Fecha y hora de fin del rango de búsqueda (formato: YYYY-MM-DD HH:MM:SS)"
    )

    location_id: Optional[int] = Field(
        None, description="ID de la ubicación para filtrar las citas (opcional)"
    )

    @validator("end_date")
    def validate_date_range(cls, v: datetime, values: Dict[str, Any]) -> datetime:
        """Valida que end_date sea posterior a start_date"""
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("end_date debe ser posterior a start_date")
        return v

    class Config:
        extra = "forbid"
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else None
        }
