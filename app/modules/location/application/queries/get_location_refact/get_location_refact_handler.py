from typing import Optional
from pydantic import BaseModel, Field


class FindAllLocationQuery(BaseModel):
    page_index: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1)
    order_by: str = Field(default="id")
    sort_by: str = Field(default="asc")
    query: Optional[str] = Field(default=None)
    fields: Optional[list[str]] = Field(default=None)
