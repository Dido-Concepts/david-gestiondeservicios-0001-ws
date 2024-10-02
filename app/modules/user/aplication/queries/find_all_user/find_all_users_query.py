from pydantic import BaseModel, Field


class FindAllUsersQuery(BaseModel):
    page_index: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1)
