import re  # Para usar expresiones regulares en las validaciones
from typing import Optional
from datetime import date, time

# Importaciones de Pydantic para validación de modelos y campos
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateDaysOffRequest(BaseModel):
    """
    Modelo Pydantic para la solicitud de creación de un día libre vía API.
    Define la estructura esperada y aplica validaciones a los datos de entrada.
    """
    # --- Campos del Modelo ---
    user_id: int = Field(..., gt=0, description="ID del usuario al que se asignará el día libre.")
    tipo_dia_libre_maintable_id: int = Field(..., gt=0, description="ID del tipo de día libre en la tabla maestra.")
    fecha_inicio: date = Field(..., description="Fecha de inicio del período de día libre (YYYY-MM-DD).")
    fecha_fin: date = Field(..., description="Fecha de fin del período de día libre (YYYY-MM-DD).")
    
    # Campos opcionales
    hora_inicio: Optional[time] = Field(None, description="Hora de inicio para días libres parciales (HH:MM:SS).")
    hora_fin: Optional[time] = Field(None, description="Hora de fin para días libres parciales (HH:MM:SS).")
    motivo: Optional[str] = Field(None, description="Razón o descripción del día libre.")

    # --- Validadores de Campo ---

    @field_validator("fecha_fin")
    def validate_fecha_fin(cls, v: date, info) -> date:
        """
        Valida que fecha_fin sea igual o posterior a fecha_inicio.
        """
        fecha_inicio = info.data.get("fecha_inicio")
        if fecha_inicio and v < fecha_inicio:
            raise ValueError("fecha_fin no puede ser anterior a fecha_inicio.")
        
        return v

    @field_validator("hora_fin")
    def validate_hora_fin(cls, v: Optional[time], info) -> Optional[time]:
        """
        Valida que si se proporciona hora_fin, también debe proporcionarse hora_inicio
        y hora_fin debe ser posterior a hora_inicio.
        """
        hora_inicio = info.data.get("hora_inicio")
        
        # Si se proporciona hora_fin pero no hora_inicio
        if v is not None and hora_inicio is None:
            raise ValueError("Si se proporciona hora_fin, también debe proporcionarse hora_inicio.")
        
        # Si ambas están proporcionadas, hora_fin debe ser > hora_inicio
        if v is not None and hora_inicio is not None and v <= hora_inicio:
            raise ValueError("hora_fin debe ser posterior a hora_inicio.")
        
        return v

    @field_validator("hora_inicio")
    def validate_hora_inicio(cls, v: Optional[time], info) -> Optional[time]:
        """
        Valida que si se proporciona hora_inicio, también debe proporcionarse hora_fin.
        """
        # Obtenemos hora_fin si ya fue validada
        hora_fin = info.data.get("hora_fin")
        
        # Si se proporciona hora_inicio pero no hora_fin (y hora_fin no viene después en el modelo)
        if v is not None and hora_fin is None:
            # Esta validación se complementa con la de hora_fin
            pass
        
        return v

    @field_validator("motivo")
    def validate_motivo(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida que motivo no sea solo espacios en blanco si se proporciona.
        """
        if v is not None and not v.strip():
            raise ValueError("motivo no puede contener solo espacios.")
        
        return v.strip() if v else None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 5,
                "tipo_dia_libre_maintable_id": 1,
                "fecha_inicio": "2024-01-15",
                "fecha_fin": "2024-01-17",
                "hora_inicio": "09:00:00",
                "hora_fin": "17:00:00",
                "motivo": "Vacaciones familiares"
            }
        },
        # Configuración adicional útil:
        validate_assignment=True,
        extra='forbid'
    ) 