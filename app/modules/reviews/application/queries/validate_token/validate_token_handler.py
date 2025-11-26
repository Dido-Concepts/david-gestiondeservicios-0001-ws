from datetime import datetime
from typing import Optional

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.reviews.domain.repositories.review_repository import ReviewRepository
from app.modules.share.domain.handler.request_handler import IRequestHandler


class ValidateTokenQuery(BaseModel):
    """
    Query para validar un token de review.
    """
    token: str


class ValidateTokenQueryResponse(BaseModel):
    """
    Respuesta del query de validación de token.
    """
    valid: bool
    review_id: Optional[int]
    appointment_id: Optional[int]
    customer_name: Optional[str]
    service_name: Optional[str]
    user_name: Optional[str]
    start_datetime: Optional[datetime]
    location_name: Optional[str]
    already_reviewed: bool
    token_expired: bool
    message: str


@Mediator.handler
class ValidateTokenQueryHandler(
    IRequestHandler[ValidateTokenQuery, ValidateTokenQueryResponse]
):
    """
    Manejador para el query ValidateTokenQuery.
    Valida un token de review y retorna información de la cita.
    """

    def __init__(self) -> None:
        injector = injector_var.get()
        self.review_repository: ReviewRepository = injector.get(ReviewRepository)  # type: ignore[type-abstract]

    async def handle(self, query: ValidateTokenQuery) -> ValidateTokenQueryResponse:
        result = await self.review_repository.validate_token(
            token=query.token,
        )

        return ValidateTokenQueryResponse(
            valid=result.valid,
            review_id=result.review_id,
            appointment_id=result.appointment_id,
            customer_name=result.customer_name,
            service_name=result.service_name,
            user_name=result.user_name,
            start_datetime=result.start_datetime,
            location_name=result.location_name,
            already_reviewed=result.already_reviewed,
            token_expired=result.token_expired,
            message=result.message,
        )
