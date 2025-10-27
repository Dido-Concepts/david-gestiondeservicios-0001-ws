import json
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import create_session
from app.modules.auth.domain.models.app_to_app_auth_domain import AppToAppAuth
from app.modules.share.utils.handle_dbapi_error import handle_error


class AppToAppDirectService:
    """
    Servicio directo para validación de tokens app-to-app que maneja
    explícitamente las conexiones de base de datos sin usar repositorio ni UnitOfWork.
    Este servicio es específico para operaciones de autenticación críticas.
    """

    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key

    async def validate_token(self, token: str) -> AppToAppAuth:
        """
        Valida un token directamente contra la base de datos.
        Abre y cierra explícitamente la conexión de base de datos.
        """
        session: Optional[AsyncSession] = None

        try:
            # Crear sesión explícitamente
            session = await create_session()

            stmt = text(
                """
                SELECT app_name, token, is_valid, allowed_scopes, expires_at
                FROM sp_validate_app_token(:p_token)
                """
            )

            params = {"p_token": token}

            result = await session.execute(stmt, params)
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

        except Exception:
            # Para cualquier otro error, retornar token inválido
            return AppToAppAuth(
                app_name="",
                token=token,
                scopes=[],
                is_valid=False,
            )

        finally:
            # Cerrar explícitamente la sesión
            if session:
                await session.close()

    async def get_token_info(self, token: str) -> Optional[dict[str, Any]]:
        """
        Obtiene información básica de un token directamente de la base de datos.
        Abre y cierra explícitamente la conexión de base de datos.
        """
        session: Optional[AsyncSession] = None

        try:
            # Crear sesión explícitamente
            session = await create_session()

            stmt = text(
                """
                SELECT token_id, app_name, token, is_active, created_at,
                       expires_at, last_used_at, description, allowed_scopes
                FROM sp_get_app_token_info(:p_token)
                """
            )

            params = {"p_token": token}

            result = await session.execute(stmt, params)
            row = result.fetchone()

            if row is None:
                return None

            # Parsear allowed_scopes desde JSON
            allowed_scopes = row[8] if row[8] else []

            return {
                "token_id": row[0],
                "app_name": row[1],
                "token": row[2],
                "is_active": row[3],
                "created_at": row[4],
                "expires_at": row[5],
                "last_used_at": row[6],
                "description": row[7],
                "allowed_scopes": allowed_scopes,
            }

        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError("Este punto nunca se alcanza")

        except Exception:
            # Para cualquier otro error, retornar None
            return None

        finally:
            # Cerrar explícitamente la sesión
            if session:
                await session.close()
