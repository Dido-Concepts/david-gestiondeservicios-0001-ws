"""
Dependencias de autenticación para FastAPI.

ARQUITECTURA DE SERVICIOS APP-TO-APP:

1. AppToAppTokenService (con UnitOfWork):
   - Usado para operaciones de gestión: crear, listar, revocar tokens
   - Depende del repositorio que usa UnitOfWork
   - Apropiado para operaciones dentro del contexto de request

2. AppToAppDirectService (sin UnitOfWork):
   - Usado EXCLUSIVAMENTE para validación de tokens durante autenticación
   - Maneja conexiones de BD explícitamente (abre/cierra)
   - NO depende de UnitOfWork para evitar problemas de contexto
   - Específico para operaciones críticas de autenticación

Esta separación garantiza que la validación de tokens app-to-app sea independiente
del contexto de UnitOfWork, evitando errores cuando el middleware no ha configurado
aún el contexto de la transacción.
"""

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
from app.modules.auth.infra.services.app_to_app_direct_service import (
    AppToAppDirectService,
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


def get_app_token_service() -> AppToAppTokenService:
    """
    Factory function para crear AppToAppTokenService dentro del contexto de UnitOfWork.
    Esta función se debe llamar solo dentro del contexto de un request donde el middleware
    ya ha configurado el UnitOfWork en uow_var.

    NOTA: Este servicio usa el repositorio con UnitOfWork y está destinado para operaciones
    de gestión de tokens (crear, listar, revocar, etc.).
    """
    app_token_repository = AppToAppTokenImplementationRepository()
    return AppToAppTokenService(APP_SECRET_KEY, app_token_repository)


def get_app_token_direct_service() -> AppToAppDirectService:
    """
    Factory function para crear AppToAppDirectService que maneja conexiones explícitamente.
    Este servicio NO usa UnitOfWork y es específico para validaciones de autenticación críticas.

    NOTA: Este servicio abre y cierra explícitamente las conexiones de BD, evitando
    dependencias del UnitOfWork durante la validación de tokens de autenticación.
    """
    return AppToAppDirectService(APP_SECRET_KEY)


def get_app_token_service_dependency() -> AppToAppTokenService:
    """
    Dependency function para FastAPI que crea AppToAppTokenService.
    Se ejecuta dentro del contexto de la request donde el UnitOfWork ya está configurado.
    """
    return get_app_token_service()


def get_app_token_direct_service_dependency() -> AppToAppDirectService:
    """
    Dependency function para FastAPI que crea AppToAppDirectService.
    Este servicio maneja conexiones de BD explícitamente sin UnitOfWork.
    """
    return get_app_token_direct_service()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    app_token_direct_service: AppToAppDirectService = Depends(
        get_app_token_direct_service_dependency
    ),
) -> UserAuth:
    """
    Obtiene información del usuario actual, soportando tanto tokens de Google como app-to-app.
    Para tokens app-to-app, asigna el nombre de la app como email.
    """
    token = credentials.credentials

    # Primero intentar con token app-to-app
    try:
        auth_result = await app_token_direct_service.validate_token(token)
        if auth_result.is_valid:
            # Crear un UserAuth con información del token app-to-app
            return UserAuth(
                email=auth_result.app_name,
                name=auth_result.app_name,
                sub=auth_result.app_name,
                iss="app_to_app",
            )
    except Exception:
        pass  # Continuar con validación de Google

    # Intentar con token de Google
    try:
        user_info = google_auth_service.verify_token(token)
        return user_info
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido",
        )


async def _validate_app_to_app_permissions(
    token: str, roles: list[str], app_token_direct_service: AppToAppDirectService
) -> bool:
    """Valida permisos de token app-to-app. Retorna True si es válido, False si no es app-to-app."""
    try:
        auth_result = await app_token_direct_service.validate_token(token)
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
        app_token_direct_service: AppToAppDirectService = Depends(
            get_app_token_direct_service_dependency
        ),
    ) -> None:
        token = credentials.credentials

        # Intentar primero con token app-to-app
        if await _validate_app_to_app_permissions(
            token, roles, app_token_direct_service
        ):
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
    app_token_direct_service: AppToAppDirectService = Depends(
        get_app_token_direct_service_dependency
    ),
) -> AppToAppAuth:
    """Validar token de aplicación a aplicación."""
    token = credentials.credentials

    try:
        auth_result = await app_token_direct_service.validate_token(token)

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
    app_token_direct_service: AppToAppDirectService = Depends(
        get_app_token_direct_service_dependency
    ),
) -> AppToAppAuth | None:
    """Dependency opcional para tokens app-to-app que no falla si el token es inválido."""

    try:
        token = credentials.credentials
        auth_result = await app_token_direct_service.validate_token(token)
        return auth_result if auth_result.is_valid else None
    except Exception:
        return None
