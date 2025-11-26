from typing import Annotated

from fastapi import APIRouter, Path
from mediatr import Mediator

from app.modules.reviews.application.commands.process_appointment_for_review.process_appointment_for_review_handler import (
    ProcessAppointmentForReviewCommand,
    ProcessAppointmentForReviewResponse,
)
from app.modules.reviews.application.commands.mark_email_sent.mark_email_sent_handler import (
    MarkEmailSentCommand,
    MarkEmailSentResponse,
)
from app.modules.reviews.application.commands.submit_review.submit_review_handler import (
    SubmitReviewCommand,
    SubmitReviewResponse,
)
from app.modules.reviews.application.queries.validate_token.validate_token_handler import (
    ValidateTokenQuery,
    ValidateTokenQueryResponse,
)
from app.modules.reviews.application.request.submit_review_request import (
    SubmitReviewRequest,
)


class ReviewsV2Controller:
    """
    Controlador que agrupa las rutas de API (versión 2) relacionadas con reviews.
    Implementa las 4 APIs para el sistema de reviews de citas.
    """

    def __init__(self, mediator: Mediator):
        """
        Constructor del controlador.
        Recibe una instancia del Mediator, que se utilizará para enviar comandos y queries.
        """
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        """
        Define y añade las rutas específicas de este controlador al router de FastAPI.
        """
        # API 1: Procesar cita para review
        self.router.post(
            "/reviews/process-appointment/{appointment_id}",
            description=(
                "Procesa una cita para verificar si debe enviarse email de review. "
                "Crea el review automáticamente si no existe."
            ),
        )(self.process_appointment_for_review)

        # API 2: Marcar email como enviado
        self.router.patch(
            "/reviews/{review_id}/mark-sent",
            description="Marca un review como email enviado.",
        )(self.mark_email_sent)

        # API 3: Validar token (FRONTEND)
        self.router.get(
            "/reviews/validate/{token}",
            description="Valida un token de review y retorna información de la cita.",
        )(self.validate_token)

        # API 4: Guardar calificación (FRONTEND)
        self.router.post(
            "/reviews/submit",
            description="Guarda la calificación del cliente.",
        )(self.submit_review)

    async def process_appointment_for_review(
        self,
        appointment_id: Annotated[int, Path(description="ID de la cita a procesar")],
    ) -> ProcessAppointmentForReviewResponse:
        """
        Procesa una cita para verificar si debe enviarse email de review.
        Crea el review automáticamente si no existe.

        Args:
            appointment_id: El ID de la cita a procesar.

        Returns:
            ProcessAppointmentForReviewResponse con el resultado del procesamiento.
        """
        command = ProcessAppointmentForReviewCommand(
            appointment_id=appointment_id,
            days_after=7,
            user_transaction="n8n",
        )

        result: ProcessAppointmentForReviewResponse = await self.mediator.send_async(command)
        return result

    async def mark_email_sent(
        self,
        review_id: Annotated[int, Path(description="ID del review a marcar como enviado")],
    ) -> MarkEmailSentResponse:
        """
        Marca un review como email enviado.
        La información del cliente se obtiene internamente del SP.

        Args:
            review_id: El ID del review a marcar.

        Returns:
            MarkEmailSentResponse con el resultado de la operación.
        """
        command = MarkEmailSentCommand(
            review_id=review_id,
            user_transaction="n8n",
        )

        result: MarkEmailSentResponse = await self.mediator.send_async(command)
        return result

    async def validate_token(
        self,
        token: Annotated[str, Path(description="Token del review a validar")],
    ) -> ValidateTokenQueryResponse:
        """
        Valida un token de review y retorna información de la cita.

        Args:
            token: El token a validar.

        Returns:
            ValidateTokenQueryResponse con la información de validación.
        """
        query = ValidateTokenQuery(token=token)

        result: ValidateTokenQueryResponse = await self.mediator.send_async(query)
        return result

    async def submit_review(
        self,
        request: SubmitReviewRequest,
    ) -> SubmitReviewResponse:
        """
        Guarda la calificación del cliente.

        Args:
            request: Los datos de la calificación (token, rating, comment).

        Returns:
            SubmitReviewResponse con el resultado de la operación.
        """
        command = SubmitReviewCommand(
            token=request.token,
            rating=request.rating,
            comment=request.comment,
            user_transaction="customer",
        )

        result: SubmitReviewResponse = await self.mediator.send_async(command)
        return result
