from datetime import datetime
from typing import Optional

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.reviews.domain.repositories.review_repository import ReviewRepository
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.share.infra.email.email_service import EmailService, EmailResult


class MarkEmailSentCommand(BaseModel):
    """
    Comando para marcar un review como email enviado.
    También envía el correo electrónico al cliente.
    La información del cliente se obtiene internamente del SP.
    """
    review_id: int
    user_transaction: str = "n8n"


class MarkEmailSentResponse(BaseModel):
    """
    Respuesta del comando de marcar email enviado.
    """
    success: bool
    review_id: int
    email_sent_at: Optional[datetime]
    message: str
    email_sent: bool = False
    email_error: Optional[str] = None


@Mediator.handler
class MarkEmailSentCommandHandler(
    IRequestHandler[MarkEmailSentCommand, MarkEmailSentResponse]
):
    """
    Manejador para el comando MarkEmailSentCommand.
    Envía el correo de review al cliente y marca el review como email enviado.
    """

    def __init__(self) -> None:
        injector = injector_var.get()
        self.review_repository: ReviewRepository = injector.get(ReviewRepository)  # type: ignore[type-abstract]
        self.email_service = EmailService()

    async def handle(self, command: MarkEmailSentCommand) -> MarkEmailSentResponse:
        # Primero obtener la información del review y cliente desde el SP
        review_info = await self.review_repository.get_review_info_for_email(
            review_id=command.review_id,
        )
        
        # Si no se encontró el review o no tiene la información necesaria
        if not review_info.success or not review_info.customer_email:
            return MarkEmailSentResponse(
                success=False,
                review_id=command.review_id,
                email_sent_at=None,
                message=review_info.message,
                email_sent=False,
                email_error="No se pudo obtener información del review",
            )
        
        # Enviar el correo electrónico con la información obtenida del SP
        email_result: EmailResult = await self.email_service.send_review_email(
            to_email=review_info.customer_email,
            to_name=review_info.customer_name or "",
            review_token=review_info.review_token or "",
            customer_name=review_info.customer_name or "",
        )
        
        # Si el correo se envió exitosamente, marcar en la base de datos
        if email_result.success:
            result = await self.review_repository.mark_email_sent(
                review_id=command.review_id,
                user_transaction=command.user_transaction,
            )

            return MarkEmailSentResponse(
                success=result.success,
                review_id=result.review_id,
                email_sent_at=result.email_sent_at,
                message=result.message,
                email_sent=True,
                email_error=None,
            )
        else:
            # Si falló el envío del correo, retornar error sin marcar en BD
            return MarkEmailSentResponse(
                success=False,
                review_id=command.review_id,
                email_sent_at=None,
                message=f"Error al enviar correo: {email_result.message}",
                email_sent=False,
                email_error=email_result.error,
            )
