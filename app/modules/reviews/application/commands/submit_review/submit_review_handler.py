from typing import Optional

from mediatr import Mediator
from pydantic import BaseModel, Field

from app.constants import injector_var
from app.modules.reviews.domain.repositories.review_repository import ReviewRepository
from app.modules.share.domain.handler.request_handler import IRequestHandler


class SubmitReviewCommand(BaseModel):
    """
    Comando para guardar la calificación del cliente.
    """
    token: str
    rating: int = Field(ge=1, le=5, description="Calificación del 1 al 5")
    comment: Optional[str] = None
    user_transaction: str = "customer"


class SubmitReviewResponse(BaseModel):
    """
    Respuesta del comando de enviar review.
    """
    success: bool
    review_id: Optional[int]
    message: str


@Mediator.handler
class SubmitReviewCommandHandler(
    IRequestHandler[SubmitReviewCommand, SubmitReviewResponse]
):
    """
    Manejador para el comando SubmitReviewCommand.
    Guarda la calificación del cliente.
    """

    def __init__(self) -> None:
        injector = injector_var.get()
        self.review_repository: ReviewRepository = injector.get(ReviewRepository)  # type: ignore[type-abstract]

    async def handle(self, command: SubmitReviewCommand) -> SubmitReviewResponse:
        result = await self.review_repository.submit_review(
            token=command.token,
            rating=command.rating,
            comment=command.comment,
            user_transaction=command.user_transaction,
        )

        return SubmitReviewResponse(
            success=result.success,
            review_id=result.review_id,
            message=result.message,
        )
