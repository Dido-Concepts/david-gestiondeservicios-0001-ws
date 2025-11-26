from typing import Optional

from pydantic import BaseModel, Field


class SubmitReviewRequest(BaseModel):
    """
    Request para enviar una calificación de review.
    """
    token: str = Field(..., description="Token único del review")
    rating: int = Field(..., ge=1, le=5, description="Calificación del 1 al 5")
    comment: Optional[str] = Field(None, description="Comentario opcional del cliente")
