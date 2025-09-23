from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.modules.auth.application.app_to_app_use_cases import (
    CreateAppToAppTokenUseCase,
    GetAppToAppTokenInfoUseCase,
    ListAppToAppTokensUseCase,
    RevokeAppToAppTokenUseCase,
    ValidateAppToAppTokenUseCase,
)
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
    app_token_service,  # Usar la instancia compartida
)

router = APIRouter(prefix="/auth/app-to-app", tags=["App-to-App Authentication"])

# Usar la instancia compartida del servicio
token_service = app_token_service


# Modelos Pydantic para las requests/responses
class CreateTokenRequest(BaseModel):
    app_name: str
    description: Optional[str] = None
    expires_in_days: Optional[int] = None
    allowed_scopes: Optional[list[str]] = None


class TokenResponse(BaseModel):
    app_name: str
    token: str
    is_active: bool
    created_at: str
    expires_at: Optional[str] = None
    description: Optional[str] = None
    allowed_scopes: Optional[list[str]] = None


class TokenValidationRequest(BaseModel):
    token: str
    required_scope: Optional[str] = None


class TokenValidationResponse(BaseModel):
    app_name: str
    is_valid: bool
    scopes: list[str]
    expires_at: Optional[str] = None


class RevokeTokenRequest(BaseModel):
    token: str


@router.post(
    "/tokens", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def create_app_token(
    request: CreateTokenRequest,
    _: None = Depends(permission_required(["admin"])),
):
    """Crear un nuevo token de aplicación a aplicación."""

    try:
        use_case = CreateAppToAppTokenUseCase(token_service)
        token = await use_case.execute(
            app_name=request.app_name,
            description=request.description,
            expires_in_days=request.expires_in_days,
            allowed_scopes=request.allowed_scopes,
        )

        return TokenResponse(
            app_name=token.app_name,
            token=token.token,
            is_active=token.is_active,
            created_at=token.created_at.isoformat(),
            expires_at=token.expires_at.isoformat() if token.expires_at else None,
            description=token.description,
            allowed_scopes=token.allowed_scopes,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/tokens/validate", response_model=TokenValidationResponse)
async def validate_app_token(request: TokenValidationRequest):
    """Validar un token de aplicación a aplicación."""

    try:
        use_case = ValidateAppToAppTokenUseCase(token_service)
        auth_result = await use_case.execute(
            token=request.token,
            required_scope=request.required_scope,
        )

        return TokenValidationResponse(
            app_name=auth_result.app_name,
            is_valid=auth_result.is_valid,
            scopes=auth_result.scopes,
            expires_at=(
                auth_result.expires_at.isoformat() if auth_result.expires_at else None
            ),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/tokens", response_model=list[TokenResponse])
async def list_app_tokens(
    app_name: Optional[str] = None,
    _: None = Depends(permission_required(["admin"])),
):
    """Listar tokens de aplicación a aplicación."""

    use_case = ListAppToAppTokensUseCase(token_service)
    tokens = await use_case.execute(app_name=app_name)

    return [
        TokenResponse(
            app_name=token.app_name,
            token=token.token,
            is_active=token.is_active,
            created_at=token.created_at.isoformat(),
            expires_at=token.expires_at.isoformat() if token.expires_at else None,
            description=token.description,
            allowed_scopes=token.allowed_scopes,
        )
        for token in tokens
    ]


@router.get("/tokens/{token}", response_model=TokenResponse)
async def get_app_token_info(
    token: str,
    _: None = Depends(permission_required(["admin"])),
):
    """Obtener información de un token específico."""

    try:
        use_case = GetAppToAppTokenInfoUseCase(token_service)
        token_info = await use_case.execute(token=token)

        if not token_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token no encontrado",
            )

        return TokenResponse(
            app_name=token_info.app_name,
            token=token_info.token,
            is_active=token_info.is_active,
            created_at=token_info.created_at.isoformat(),
            expires_at=(
                token_info.expires_at.isoformat() if token_info.expires_at else None
            ),
            description=token_info.description,
            allowed_scopes=token_info.allowed_scopes,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/tokens", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_app_token(
    request: RevokeTokenRequest,
    _: None = Depends(permission_required(["admin"])),
):
    """Revocar un token de aplicación a aplicación."""

    try:
        use_case = RevokeAppToAppTokenUseCase(token_service)
        success = await use_case.execute(token=request.token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token no encontrado",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/tokens/debug")
async def debug_auth():
    """Endpoint de debug temporal para probar autenticación."""
    return {
        "message": "Debug endpoint accessible",
        "token_service_initialized": token_service is not None,
        "current_tokens": len(token_service._tokens),
        "tokens_list": list(token_service._tokens.keys()),
    }
