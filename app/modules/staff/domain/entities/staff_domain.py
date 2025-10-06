from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class RoleEntity:
    """
    Entidad que representa un rol del staff.
    """

    role_id: int
    role_name: str


@dataclass
class StaffEntity:
    """
    Entidad de dominio que representa un miembro del staff obtenido desde la base de datos.
    Corresponde a la estructura devuelta por el stored procedure 'staff_get_all'.
    """

    id: int
    user_name: str
    email: str
    status: str
    location_id: int
    location_name: str
    roles: List[RoleEntity]
    created_at: datetime
    updated_at: Optional[datetime]
