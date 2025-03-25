from os import getenv
from typing import Awaitable, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.constants import injector_var
from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.infra.services.google_auth_service import GoogleAuthService
from app.modules.user.domain.repositories.user_repository import UserRepository

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


def permission_required(roles: list[str]) -> Callable[..., Awaitable[None]]:
    async def permission_verifier(user: UserAuth = Depends(get_current_user)) -> None:

        if not user.email:
            raise ValueError("User email not found in token")

        injector = injector_var.get()

        user_repository = injector.get(UserRepository)  # type: ignore[type-abstract]

        user_db = await user_repository.find_user_by_email(email=user.email)
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

    return permission_verifier
