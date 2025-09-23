from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AppToAppToken:
    """Modelo de dominio para tokens de aplicación a aplicación."""

    app_name: str
    token: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    description: Optional[str] = None
    allowed_scopes: Optional[list[str]] = None


@dataclass
class AppToAppAuth:
    """Modelo de autenticación para tokens app-to-app."""

    app_name: str
    token: str
    scopes: list[str]
    is_valid: bool
    expires_at: Optional[datetime] = None
