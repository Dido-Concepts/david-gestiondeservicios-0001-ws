from pydantic import BaseModel


class FindRolPermissionQuery(BaseModel):
    email: str
