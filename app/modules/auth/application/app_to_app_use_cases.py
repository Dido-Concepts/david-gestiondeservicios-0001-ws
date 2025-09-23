from typing import Optional

from app.modules.auth.domain.models.app_to_app_auth_domain import (
    AppToAppAuth,
    AppToAppToken,
)
from app.modules.auth.infra.services.app_to_app_token_service import (
    AppToAppTokenService,
)


class CreateAppToAppTokenUseCase:
    """Caso de uso para crear tokens de aplicación a aplicación."""

    def __init__(self, token_service: AppToAppTokenService) -> None:
        self.token_service = token_service

    async def execute(
        self,
        app_name: str,
        description: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        allowed_scopes: Optional[list[str]] = None,
    ) -> AppToAppToken:
        """Crea un nuevo token para una aplicación."""

        if not app_name or not app_name.strip():
            raise ValueError("El nombre de la aplicación es requerido")

        # Validar scopes si se proporcionan
        if allowed_scopes:
            valid_scopes = ["read", "write", "admin", "api"]
            for scope in allowed_scopes:
                if scope not in valid_scopes:
                    raise ValueError(
                        f"Scope inválido: {scope}. Scopes válidos: {valid_scopes}"
                    )

        # Validar días de expiración
        if expires_in_days is not None and expires_in_days <= 0:
            raise ValueError("Los días de expiración deben ser mayor a 0")

        return self.token_service.generate_token(
            app_name=app_name.strip(),
            description=description,
            expires_in_days=expires_in_days,
            allowed_scopes=allowed_scopes,
        )


class ValidateAppToAppTokenUseCase:
    """Caso de uso para validar tokens de aplicación a aplicación."""

    def __init__(self, token_service: AppToAppTokenService) -> None:
        self.token_service = token_service

    async def execute(
        self, token: str, required_scope: Optional[str] = None
    ) -> AppToAppAuth:
        """Valida un token y opcionalmente verifica permisos de scope."""

        if not token or not token.strip():
            raise ValueError("El token es requerido")

        # Validar el token
        auth_result = self.token_service.validate_token(token.strip())

        # Si el token es válido y se requiere un scope específico, verificarlo
        if auth_result.is_valid and required_scope:
            if required_scope not in auth_result.scopes:
                auth_result.is_valid = False

        return auth_result


class RevokeAppToAppTokenUseCase:
    """Caso de uso para revocar tokens de aplicación a aplicación."""

    def __init__(self, token_service: AppToAppTokenService) -> None:
        self.token_service = token_service

    async def execute(self, token: str) -> bool:
        """Revoca un token específico."""

        if not token or not token.strip():
            raise ValueError("El token es requerido")

        return self.token_service.revoke_token(token.strip())


class ListAppToAppTokensUseCase:
    """Caso de uso para listar tokens de aplicación a aplicación."""

    def __init__(self, token_service: AppToAppTokenService) -> None:
        self.token_service = token_service

    async def execute(self, app_name: Optional[str] = None) -> list[AppToAppToken]:
        """Lista tokens, opcionalmente filtrados por aplicación."""

        return self.token_service.list_tokens(app_name)


class GetAppToAppTokenInfoUseCase:
    """Caso de uso para obtener información de un token específico."""

    def __init__(self, token_service: AppToAppTokenService) -> None:
        self.token_service = token_service

    async def execute(self, token: str) -> Optional[AppToAppToken]:
        """Obtiene información detallada de un token."""

        if not token or not token.strip():
            raise ValueError("El token es requerido")

        return self.token_service.get_token_info(token.strip())
