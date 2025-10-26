from pydantic import BaseModel, Field


class UpsertNotificationLocationRequest(BaseModel):
    """
    Request para activar/desactivar o crear una configuración de notificación por location.
    """

    location_id: int = Field(..., description="ID de la location/sede", gt=0)
    is_active: bool = Field(
        ..., description="Estado de activación de las notificaciones"
    )


class DeactivateNotificationLocationRequest(BaseModel):
    """
    Request para desactivar las notificaciones de una location.
    """

    location_id: int = Field(..., description="ID de la location/sede", gt=0)
