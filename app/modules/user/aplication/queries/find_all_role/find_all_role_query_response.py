from pydantic import BaseModel


class FindAllRoleQueryResponse(BaseModel):
    id: int
    name: str
    description: str
