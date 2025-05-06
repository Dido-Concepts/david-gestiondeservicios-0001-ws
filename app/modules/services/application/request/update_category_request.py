from typing import Optional

from pydantic import BaseModel


class UpdateCategoryRequest(BaseModel):
    location_id: int
    name_category: str
    description_category: Optional[str] = None
