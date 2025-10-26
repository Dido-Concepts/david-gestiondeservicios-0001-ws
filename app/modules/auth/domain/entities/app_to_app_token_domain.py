from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AppToAppTokenEntity:
    """Entidad de dominio para tokens de aplicación a aplicación almacenados en BD."""

    token_id: int
    app_name: str
    token: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    description: Optional[str] = None
    allowed_scopes: Optional[list[str]] = None
    insert_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    user_create: Optional[str] = None
    user_modify: Optional[str] = None
