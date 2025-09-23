import secrets
from datetime import datetime, timedelta
from typing import Optional

from app.modules.auth.domain.models.app_to_app_auth_domain import (
    AppToAppAuth,
    AppToAppToken,
)

# Token storage compartido (en producción esto iría en base de datos)
_shared_tokens: dict[str, AppToAppToken] = {}


class AppToAppTokenService:
    """Servicio para gestionar tokens de aplicación a aplicación."""

    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key
        self.token_prefix = "app_"
        # Usar el storage compartido en lugar de instancia local
        self._tokens = _shared_tokens

    def generate_token(
        self,
        app_name: str,
        description: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        allowed_scopes: Optional[list[str]] = None,
    ) -> AppToAppToken:
        """Genera un nuevo token para una aplicación."""

        # Generar token único
        raw_token = secrets.token_urlsafe(32)
        token = f"{self.token_prefix}{raw_token}"

        # Calcular fecha de expiración
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Crear el token
        app_token = AppToAppToken(
            app_name=app_name,
            token=token,
            is_active=True,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            description=description,
            allowed_scopes=allowed_scopes or [],
        )

        # Almacenar el token (en producción esto iría a BD)
        self._tokens[token] = app_token

        return app_token

    def validate_token(self, token: str) -> AppToAppAuth:
        """Valida un token y retorna la información de autenticación."""

        # Verificar si el token existe
        if token not in self._tokens:
            return AppToAppAuth(
                app_name="",
                token=token,
                scopes=[],
                is_valid=False,
            )

        app_token = self._tokens[token]

        # Verificar si el token está activo
        if not app_token.is_active:
            return AppToAppAuth(
                app_name=app_token.app_name,
                token=token,
                scopes=[],
                is_valid=False,
            )

        # Verificar si el token ha expirado
        if app_token.expires_at and datetime.utcnow() > app_token.expires_at:
            return AppToAppAuth(
                app_name=app_token.app_name,
                token=token,
                scopes=[],
                is_valid=False,
                expires_at=app_token.expires_at,
            )

        # Actualizar último uso
        app_token.last_used_at = datetime.utcnow()

        return AppToAppAuth(
            app_name=app_token.app_name,
            token=token,
            scopes=app_token.allowed_scopes or [],
            is_valid=True,
            expires_at=app_token.expires_at,
        )

    def revoke_token(self, token: str) -> bool:
        """Revoca un token desactivándolo."""
        if token in self._tokens:
            self._tokens[token].is_active = False
            return True
        return False

    def list_tokens(self, app_name: Optional[str] = None) -> list[AppToAppToken]:
        """Lista todos los tokens, opcionalmente filtrados por app_name."""
        tokens = list(self._tokens.values())

        if app_name:
            tokens = [t for t in tokens if t.app_name == app_name]

        return tokens

    def get_token_info(self, token: str) -> Optional[AppToAppToken]:
        """Obtiene información detallada de un token."""
        return self._tokens.get(token)
