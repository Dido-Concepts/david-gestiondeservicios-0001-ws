from os import getenv
from typing import Any, Awaitable, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.auth.aplication.queries.find_rol_permission.find_rol_permission_query import (
    FindRolPermissionQuery,
)
from app.modules.auth.aplication.queries.find_rol_permission.find_rol_permission_query_handler import (
    FindRolPermissionQueryHandler,
)
from app.modules.auth.aplication.queries.find_rol_permission.find_rol_permission_query_response import (
    FindRolPermissionQueryResponse,
)
from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.infra.services.google_auth_service import GoogleAuthService
from app.modules.share.aplication.mediator.mediator import Mediator
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.infra.persistence.unit_of_work_instance import get_uow
from app.modules.user.domain.repositories.role_repository import RoleRepository
from app.modules.user.domain.repositories.user_repository import UserRepository
from app.modules.user.infra.repositories.role_implementation_repository import (
    RoleImplementationRepository,
)
from app.modules.user.infra.repositories.user_implementation_repository import (
    UserImplementationRepository,
)

GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID", "")
security = HTTPBearer()
google_auth_service = GoogleAuthService(GOOGLE_CLIENT_ID)


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


async def get_user_repository(
    uow: UnitOfWork = Depends(get_uow),
) -> UserRepository:
    return UserImplementationRepository(uow)


async def get_role_repository(
    uow: UnitOfWork = Depends(get_uow),
) -> RoleRepository:
    return RoleImplementationRepository(uow)


async def get_auth_mediator(
    user_repository: UserRepository = Depends(get_user_repository),
    role_repository: RoleRepository = Depends(get_role_repository),
) -> Mediator[Any, Any]:
    mediator: Mediator[Any, Any] = Mediator()

    mediator.register_handler(
        FindRolPermissionQuery,
        FindRolPermissionQueryHandler(
            user_repository=user_repository, role_repository=role_repository
        ),
    )

    return mediator


def permission_required(permission: str) -> Callable[..., Awaitable[None]]:
    async def permission_verifier(
        user: UserAuth = Depends(get_current_user),
        mediator: Mediator[
            FindRolPermissionQuery, FindRolPermissionQueryResponse
        ] = Depends(get_auth_mediator),
    ) -> None:

        if not user.email:
            raise ValueError("User email not found in token")

        result = await mediator.send(request=FindRolPermissionQuery(email=user.email))

        if result.permissions is None or permission not in result.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción",
            )

    return permission_verifier
