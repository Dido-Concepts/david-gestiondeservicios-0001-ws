import secrets
from datetime import datetime, timedelta
from typing import Optional

from app.modules.auth.domain.models.app_to_app_auth_domain import (
    AppToAppAuth,
    AppToAppToken,
)
from app.modules.auth.domain.repositories.app_to_app_token_repository import (
    AppToAppTokenRepository,
)


class AppToAppTokenService:
    """Servicio para gestionar tokens de aplicación a aplicación usando repositorio."""

    def __init__(self, secret_key: str, repository: AppToAppTokenRepository) -> None:
        self.secret_key = secret_key
        self.token_prefix = "app_"
        self.repository = repository

    async def generate_token(
        self,
        app_name: str,
        description: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        allowed_scopes: Optional[list[str]] = None,
        user_create: str = "system",
    ) -> AppToAppToken:
        """Genera un nuevo token para una aplicación."""

        # Generar token único
        raw_token = secrets.token_urlsafe(32)
        token = f"{self.token_prefix}{raw_token}"

        # Calcular fecha de expiración
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Crear el token en la base de datos
        await self.repository.create_token(
            app_name=app_name,
            token=token,
            expires_at=expires_at,
            description=description,
            allowed_scopes=allowed_scopes or [],
            user_create=user_create,
        )

        # Crear el objeto de respuesta
        app_token = AppToAppToken(
            app_name=app_name,
            token=token,
            is_active=True,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            description=description,
            allowed_scopes=allowed_scopes or [],
        )

        return app_token

    async def validate_token(self, token: str) -> AppToAppAuth:
        """Valida un token y retorna la información de autenticación."""
        return await self.repository.validate_token(token)

    async def revoke_token(self, token: str, user_modify: str = "system") -> bool:
        """Revoca un token desactivándolo."""
        return await self.repository.revoke_token(token, user_modify)

    async def list_tokens(self, app_name: Optional[str] = None) -> list[AppToAppToken]:
        """Lista todos los tokens, opcionalmente filtrados por app_name."""
        # Usar la implementación del repositorio con paginación
        response = await self.repository.list_tokens(
            page_index=0,
            page_size=1000,  # Por ahora traemos todos
            app_name=app_name,
        )

        # Convertir de AppToAppTokenEntity a AppToAppToken
        tokens = []
        for entity in response.data:
            token = AppToAppToken(
                app_name=entity.app_name,
                token=entity.token,
                is_active=entity.is_active,
                created_at=entity.created_at,
                expires_at=entity.expires_at,
                last_used_at=entity.last_used_at,
                description=entity.description,
                allowed_scopes=entity.allowed_scopes,
            )
            tokens.append(token)

        return tokens

    async def get_token_info(self, token: str) -> Optional[AppToAppToken]:
        """Obtiene información detallada de un token."""
        entity = await self.repository.get_token_info(token)

        if not entity:
            return None

        return AppToAppToken(
            app_name=entity.app_name,
            token=entity.token,
            is_active=entity.is_active,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            last_used_at=entity.last_used_at,
            description=entity.description,
            allowed_scopes=entity.allowed_scopes,
        )
