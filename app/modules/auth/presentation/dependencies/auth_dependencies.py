from os import getenv
from typing import Awaitable, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.constants import injector_var
from app.modules.auth.domain.models.app_to_app_auth_domain import AppToAppAuth
from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.infra.repositories.app_to_app_token_implementation_repository import (
    AppToAppTokenImplementationRepository,
)
from app.modules.auth.infra.services.app_to_app_token_service import (
    AppToAppTokenService,
)
from app.modules.auth.infra.services.google_auth_service import GoogleAuthService
from app.modules.user.domain.repositories.user_repository import UserRepository

GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID", "")
APP_SECRET_KEY = getenv("APP_SECRET_KEY", "your-secret-key-here")

security = HTTPBearer()
google_auth_service = GoogleAuthService(GOOGLE_CLIENT_ID)

# Crear instancia del repositorio y servicio
app_token_repository = AppToAppTokenImplementationRepository()
app_token_service = AppToAppTokenService(APP_SECRET_KEY, app_token_repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserAuth:
    token = credentials.credentials
    try:
        user_info = google_auth_service.verify_token(token)
        return user_info
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido",
        )


async def _validate_app_to_app_permissions(token: str, roles: list[str]) -> bool:
    """Valida permisos de token app-to-app. Retorna True si es válido, False si no es app-to-app."""
    try:
        auth_result = await app_token_service.validate_token(token)
        if not auth_result.is_valid:
            return False

        # Token app-to-app válido - verificar si tiene permisos de admin
        if "admin" in auth_result.scopes and "admin" in roles:
            return True  # Token app-to-app con scope admin puede acceder a rutas admin
        elif "admin" not in roles:
            return True  # Token app-to-app puede acceder a rutas no-admin
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"La aplicación '{auth_result.app_name}' no tiene permisos de administrador",
            )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception:
        return False  # No es un token app-to-app válido


async def _validate_google_user_permissions(token: str, roles: list[str]) -> None:
    """Valida permisos de usuario Google."""
    user_info = google_auth_service.verify_token(token)

    if not user_info.email:
        raise ValueError("User email not found in token")

    injector = injector_var.get()
    user_repository = injector.get(UserRepository)  # type: ignore[type-abstract]

    user_db = await user_repository.find_user_by_email(email=user_info.email)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no encontrado o sin permisos",
        )

    if user_db.role.name not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción",
        )


def permission_required(roles: list[str]) -> Callable[..., Awaitable[None]]:
    async def permission_verifier(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> None:
        token = credentials.credentials

        # Intentar primero con token app-to-app
        if await _validate_app_to_app_permissions(token, roles):
            return  # Token app-to-app válido y autorizado

        # Intentar con token de Google
        try:
            await _validate_google_user_permissions(token, roles)
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticación inválido",
            )

    return permission_verifier


async def get_app_to_app_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AppToAppAuth:
    """Validar token de aplicación a aplicación."""
    token = credentials.credentials

    try:
        auth_result = await app_token_service.validate_token(token)

        if not auth_result.is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de aplicación inválido o expirado",
            )

        return auth_result
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de aplicación inválido",
        )


def app_to_app_permission_required(
    required_scopes: list[str],
) -> Callable[..., Awaitable[None]]:
    """Dependency para verificar permisos de tokens app-to-app con scopes específicos."""

    async def scope_verifier(auth: AppToAppAuth = Depends(get_app_to_app_auth)) -> None:

        if not auth.is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de aplicación inválido",
            )

        # Verificar si la aplicación tiene al menos uno de los scopes requeridos
        if required_scopes and not any(
            scope in auth.scopes for scope in required_scopes
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"La aplicación '{auth.app_name}' no tiene permisos para esta operación. Scopes requeridos: {required_scopes}",
            )

    return scope_verifier


async def app_to_app_auth_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AppToAppAuth | None:
    """Dependency opcional para tokens app-to-app que no falla si el token es inválido."""

    try:
        token = credentials.credentials
        auth_result = await app_token_service.validate_token(token)
        return auth_result if auth_result.is_valid else None
    except Exception:
        return None
