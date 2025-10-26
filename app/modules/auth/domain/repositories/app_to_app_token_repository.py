from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from app.modules.auth.domain.entities.app_to_app_token_domain import AppToAppTokenEntity
from app.modules.auth.domain.models.app_to_app_auth_domain import AppToAppAuth
from app.modules.share.domain.repositories.repository_types import ResponseListRefactor


class AppToAppTokenRepository(ABC):
    """Repositorio abstracto para la gestión de tokens de aplicación a aplicación."""

    @abstractmethod
    async def create_token(
        self,
        app_name: str,
        token: str,
        expires_at: Optional[datetime] = None,
        description: Optional[str] = None,
        allowed_scopes: Optional[list[str]] = None,
        user_create: str = "system",
    ) -> int:
        """Crear un nuevo token de aplicación.

        Args:
            app_name: Nombre de la aplicación
            token: Token único
            expires_at: Fecha de expiración opcional
            description: Descripción opcional
            allowed_scopes: Lista de scopes permitidos
            user_create: Usuario que crea el token

        Returns:
            int: ID del token creado
        """
        pass

    @abstractmethod
    async def validate_token(self, token: str) -> AppToAppAuth:
        """Validar un token y obtener información de autenticación.

        Args:
            token: Token a validar

        Returns:
            AppToAppAuth: Información de autenticación
        """
        pass

    @abstractmethod
    async def list_tokens(
        self,
        page_index: int = 0,
        page_size: int = 50,
        app_name: Optional[str] = None,
        order_by: str = "created_at",
        sort_by: str = "DESC",
    ) -> ResponseListRefactor[AppToAppTokenEntity]:
        """Listar tokens con paginación.

        Args:
            page_index: Índice de la página
            page_size: Tamaño de la página
            app_name: Filtro opcional por nombre de aplicación
            order_by: Campo para ordenar
            sort_by: Dirección del ordenamiento

        Returns:
            ResponseListRefactor[AppToAppTokenEntity]: Lista paginada de tokens
        """
        pass

    @abstractmethod
    async def get_token_info(self, token: str) -> Optional[AppToAppTokenEntity]:
        """Obtener información detallada de un token.

        Args:
            token: Token a consultar

        Returns:
            Optional[AppToAppTokenEntity]: Información del token o None si no existe
        """
        pass

    @abstractmethod
    async def revoke_token(self, token: str, user_modify: str = "system") -> bool:
        """Revocar un token desactivándolo.

        Args:
            token: Token a revocar
            user_modify: Usuario que revoca el token

        Returns:
            bool: True si se revocó exitosamente, False si no existe
        """
        pass
