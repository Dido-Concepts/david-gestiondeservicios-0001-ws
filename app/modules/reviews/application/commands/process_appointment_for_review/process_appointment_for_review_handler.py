from typing import Optional

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.reviews.domain.repositories.review_repository import ReviewRepository
from app.modules.share.domain.handler.request_handler import IRequestHandler


class ProcessAppointmentForReviewCommand(BaseModel):
    """
    Comando para procesar una cita y verificar si debe enviarse email de review.
    """
    appointment_id: int
    days_after: int = 7
    user_transaction: str = "n8n"


class ProcessAppointmentForReviewResponse(BaseModel):
    """
    Respuesta del comando de procesamiento de cita para review.
    """
    success: bool
    action: str
    review_id: Optional[int]
    token: Optional[str]
    customer_email: Optional[str]
    customer_name: Optional[str]
    message: str
    should_send_email: bool


@Mediator.handler
class ProcessAppointmentForReviewCommandHandler(
    IRequestHandler[ProcessAppointmentForReviewCommand, ProcessAppointmentForReviewResponse]
):
    """
    Manejador para el comando ProcessAppointmentForReviewCommand.
    Procesa una cita para verificar si debe enviarse email de review.
    """

    def __init__(self) -> None:
        injector = injector_var.get()
        self.review_repository: ReviewRepository = injector.get(ReviewRepository)  # type: ignore[type-abstract]

    async def handle(
        self, command: ProcessAppointmentForReviewCommand
    ) -> ProcessAppointmentForReviewResponse:
        result = await self.review_repository.process_appointment_for_review(
            appointment_id=command.appointment_id,
            days_after=command.days_after,
            user_transaction=command.user_transaction,
        )

        return ProcessAppointmentForReviewResponse(
            success=result.success,
            action=result.action,
            review_id=result.review_id,
            token=result.token,
            customer_email=result.customer_email,
            customer_name=result.customer_name,
            message=result.message,
            should_send_email=result.should_send_email,
        )
