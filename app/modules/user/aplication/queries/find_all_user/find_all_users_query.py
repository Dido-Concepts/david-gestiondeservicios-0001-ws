from pydantic import BaseModel


class FindAllUsersQuery(BaseModel):
    page_index: int
    page_size: int
