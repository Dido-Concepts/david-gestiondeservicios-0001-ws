from typing import Optional

from pydantic import BaseModel, Field


class CreateServiceRequest(BaseModel):
    service_name: str = Field(..., max_length=150)
    category_id: int
    price: float = Field(..., ge=0, le=9999999.99)
    duration: float = Field(..., ge=0, le=999.9)
    description: Optional[str] = None
