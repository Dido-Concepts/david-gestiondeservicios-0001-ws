from abc import ABC, abstractmethod
from typing import Optional

from app.modules.reviews.domain.entities.review_entity import (
    ProcessAppointmentForReviewResponse,
    MarkEmailSentResponse,
    ValidateTokenResponse,
    SubmitReviewResponse,
    ReviewInfoForEmailResponse,
)


class ReviewRepository(ABC):
    """
    Clase Base Abstracta (ABC) que define la interfaz del repositorio
    para las operaciones de datos relacionadas con reviews.
    Las implementaciones concretas (que interactúan con la base de datos)
    deberán implementar los métodos aquí definidos.
    """

    @abstractmethod
    async def process_appointment_for_review(
        self,
        appointment_id: int,
        days_after: int,
        user_transaction: str,
    ) -> ProcessAppointmentForReviewResponse:
        """
        Procesa una cita para verificar si debe enviarse email de review.
        Crea el review automáticamente si no existe.

        Args:
            appointment_id: El ID de la cita a procesar.
            days_after: Días después de la cita para considerar el envío.
            user_transaction: Identificador del usuario o sistema que realiza la operación.

        Returns:
            ProcessAppointmentForReviewResponse con el resultado del procesamiento.
        """
        pass

    @abstractmethod
    async def mark_email_sent(
        self,
        review_id: int,
        user_transaction: str,
    ) -> MarkEmailSentResponse:
        """
        Marca un review como email enviado.

        Args:
            review_id: El ID del review a marcar.
            user_transaction: Identificador del usuario o sistema que realiza la operación.

        Returns:
            MarkEmailSentResponse con el resultado de la operación.
        """
        pass

    @abstractmethod
    async def get_review_info_for_email(
        self,
        review_id: int,
    ) -> ReviewInfoForEmailResponse:
        """
        Obtiene la información del review necesaria para enviar el email.

        Args:
            review_id: El ID del review.

        Returns:
            ReviewInfoForEmailResponse con la información del review, cliente y cita.
        """
        pass

    @abstractmethod
    async def validate_token(
        self,
        token: str,
    ) -> ValidateTokenResponse:
        """
        Valida un token de review y retorna información de la cita.

        Args:
            token: El token a validar.

        Returns:
            ValidateTokenResponse con la información de validación.
        """
        pass

    @abstractmethod
    async def submit_review(
        self,
        token: str,
        rating: int,
        comment: Optional[str],
        user_transaction: str,
    ) -> SubmitReviewResponse:
        """
        Guarda la calificación del cliente.

        Args:
            token: El token del review.
            rating: La calificación (1-5).
            comment: Comentario opcional del cliente.
            user_transaction: Identificador del usuario o sistema que realiza la operación.

        Returns:
            SubmitReviewResponse con el resultado de la operación.
        """
        pass
