from typing import List, Optional

from pydantic import BaseModel


class FindRolPermissionQueryResponse(BaseModel):
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
