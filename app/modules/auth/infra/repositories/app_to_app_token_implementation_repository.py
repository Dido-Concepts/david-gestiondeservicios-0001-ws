import json
from datetime import datetime
from typing import Optional

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.constants import uow_var
from app.modules.auth.domain.entities.app_to_app_token_domain import AppToAppTokenEntity
from app.modules.auth.domain.models.app_to_app_auth_domain import AppToAppAuth
from app.modules.auth.domain.repositories.app_to_app_token_repository import (
    AppToAppTokenRepository,
)
from app.modules.share.domain.repositories.repository_types import ResponseListRefactor
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error


class AppToAppTokenImplementationRepository(AppToAppTokenRepository):
    """
    Implementación concreta de la interfaz AppToAppTokenRepository usando SQLAlchemy
    y un patrón Unit of Work, interactuando con una base de datos PostgreSQL.
    Esta clase contiene el código real para interactuar con la base de datos.
    """

    @property
    def _uow(self) -> UnitOfWork:
        """Proporciona acceso a la instancia actual de UnitOfWork."""
        try:
            return uow_var.get()
        except LookupError:
            raise RuntimeError("UnitOfWork no encontrado en el contexto")

    async def create_token(
        self,
        app_name: str,
        token: str,
        expires_at: Optional[datetime] = None,
        description: Optional[str] = None,
        allowed_scopes: Optional[list[str]] = None,
        user_create: str = "system",
    ) -> int:
        """
        Implementación concreta del método para crear un nuevo token.
        Llama al stored procedure 'sp_create_app_token' de PostgreSQL.
        """
        stmt = text(
            """
            SELECT sp_create_app_token(
                :p_app_name, :p_token, :p_expires_at, :p_description,
                :p_allowed_scopes, :p_user_create
            )
            """
        )

        # Convertir allowed_scopes a JSONB
        allowed_scopes_json = json.dumps(allowed_scopes) if allowed_scopes else "[]"

        params = {
            "p_app_name": app_name,
            "p_token": token,
            "p_expires_at": expires_at,
            "p_description": description,
            "p_allowed_scopes": allowed_scopes_json,
            "p_user_create": user_create,
        }

        try:
            result = await self._uow.session.execute(stmt, params)
            row = result.fetchone()

            if row is None:
                raise RuntimeError("No se pudo crear el token")

            token_id: int = row[0]
            return token_id

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def validate_token(self, token: str) -> AppToAppAuth:
        """
        Implementación concreta del método para validar un token.
        Llama al stored procedure 'sp_validate_app_token' de PostgreSQL.
        """
        stmt = text(
            """
            SELECT app_name, token, is_valid, allowed_scopes, expires_at
            FROM sp_validate_app_token(:p_token)
            """
        )

        params = {"p_token": token}

        try:
            result = await self._uow.session.execute(stmt, params)
            row = result.fetchone()

            if row is None:
                return AppToAppAuth(
                    app_name="",
                    token=token,
                    scopes=[],
                    is_valid=False,
                )

            # Parsear allowed_scopes desde JSON
            allowed_scopes = row[3] if row[3] else []
            if isinstance(allowed_scopes, str):
                allowed_scopes = json.loads(allowed_scopes)

            return AppToAppAuth(
                app_name=row[0],
                token=row[1],
                is_valid=row[2],
                scopes=allowed_scopes,
                expires_at=row[4],
            )

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def list_tokens(
        self,
        page_index: int = 0,
        page_size: int = 50,
        app_name: Optional[str] = None,
        order_by: str = "created_at",
        sort_by: str = "DESC",
    ) -> ResponseListRefactor[AppToAppTokenEntity]:
        """
        Implementación concreta del método para listar tokens con paginación.
        Llama al stored procedure 'sp_list_app_tokens' de PostgreSQL.
        """
        stmt = text(
            """
            SELECT data, total_items
            FROM sp_list_app_tokens(
                :p_page_index, :p_page_size, :p_app_name, :p_order_by, :p_sort_by
            )
            """
        )

        params = {
            "p_page_index": page_index,
            "p_page_size": page_size,
            "p_app_name": app_name,
            "p_order_by": order_by,
            "p_sort_by": sort_by,
        }

        try:
            result = await self._uow.session.execute(stmt, params)
            row = result.fetchone()

            if row is None:
                return ResponseListRefactor(data=[], total_items=0)

            data_json = row[0]
            total_items = row[1]

            tokens_list = []

            if data_json:
                for item in data_json:
                    # Parsear fechas
                    created_at = datetime.fromisoformat(item["created_at"])

                    expires_at_obj = None
                    if item.get("expires_at"):
                        expires_at_obj = datetime.fromisoformat(item["expires_at"])

                    last_used_at_obj = None
                    if item.get("last_used_at"):
                        last_used_at_obj = datetime.fromisoformat(item["last_used_at"])

                    # Parsear allowed_scopes
                    allowed_scopes = item.get("allowed_scopes", [])

                    # Crear AppToAppTokenEntity
                    token_entity = AppToAppTokenEntity(
                        token_id=item["token_id"],
                        app_name=item["app_name"],
                        token=item["token"],
                        is_active=item["is_active"],
                        created_at=created_at,
                        expires_at=expires_at_obj,
                        last_used_at=last_used_at_obj,
                        description=item.get("description"),
                        allowed_scopes=allowed_scopes,
                    )

                    tokens_list.append(token_entity)

            return ResponseListRefactor(data=tokens_list, total_items=total_items)

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def get_token_info(self, token: str) -> Optional[AppToAppTokenEntity]:
        """
        Implementación concreta del método para obtener información de un token.
        Llama al stored procedure 'sp_get_app_token_info' de PostgreSQL.
        """
        stmt = text(
            """
            SELECT token_id, app_name, token, is_active, created_at,
                   expires_at, last_used_at, description, allowed_scopes
            FROM sp_get_app_token_info(:p_token)
            """
        )

        params = {"p_token": token}

        try:
            result = await self._uow.session.execute(stmt, params)
            row = result.fetchone()

            if row is None:
                return None

            # Parsear allowed_scopes desde JSON
            allowed_scopes = row[8] if row[8] else []

            return AppToAppTokenEntity(
                token_id=row[0],
                app_name=row[1],
                token=row[2],
                is_active=row[3],
                created_at=row[4],
                expires_at=row[5],
                last_used_at=row[6],
                description=row[7],
                allowed_scopes=allowed_scopes,
            )

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

    async def revoke_token(self, token: str, user_modify: str = "system") -> bool:
        """
        Implementación concreta del método para revocar un token.
        Llama al stored procedure 'sp_revoke_app_token' de PostgreSQL.
        """
        stmt = text(
            """
            SELECT sp_revoke_app_token(:p_token, :p_user_modify)
            """
        )

        params = {
            "p_token": token,
            "p_user_modify": user_modify,
        }

        try:
            result = await self._uow.session.execute(stmt, params)
            row = result.fetchone()

            if row is None:
                return False

            success: bool = row[0]
            return success

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")
