import re  # Para usar expresiones regulares en las validaciones
from datetime import date, time

# Importaciones de Pydantic para validación de modelos y campos
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateShiftsRequest(BaseModel):
    """
    Modelo Pydantic para la solicitud de creación de un turno de trabajo vía API.
    Define la estructura esperada y aplica validaciones a los datos de entrada.
    """
    # --- Campos del Modelo ---
    user_id: int = Field(..., gt=0, description="ID del usuario al que se asignará el turno.")
    sede_id: int = Field(..., gt=0, description="ID de la sede donde se realizará el turno.")
    fecha_turno: date = Field(..., description="Fecha del turno de trabajo (YYYY-MM-DD).")
    hora_inicio: time = Field(..., description="Hora de inicio del turno (HH:MM:SS).")
    hora_fin: time = Field(..., description="Hora de fin del turno (HH:MM:SS).")

    # --- Validadores de Campo ---

    @field_validator("hora_fin")
    def validate_hora_fin(cls, v: time, info) -> time:
        """
        Valida que hora_fin sea posterior a hora_inicio.
        """
        hora_inicio = info.data.get("hora_inicio")
        if hora_inicio and v <= hora_inicio:
            raise ValueError("hora_fin debe ser posterior a hora_inicio.")
        
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 5,
                "sede_id": 2,
                "fecha_turno": "2024-01-15",
                "hora_inicio": "09:00:00",
                "hora_fin": "17:00:00"
            }
        },
        # Configuración adicional útil:
        validate_assignment=True,
        extra='forbid'
    ) 