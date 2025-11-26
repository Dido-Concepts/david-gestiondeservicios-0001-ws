from typing import Optional

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.constants import uow_var
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork
from app.modules.share.utils.handle_dbapi_error import handle_error

from app.modules.reviews.domain.repositories.review_repository import ReviewRepository
from app.modules.reviews.domain.entities.review_entity import (
    ProcessAppointmentForReviewResponse,
    MarkEmailSentResponse,
    ValidateTokenResponse,
    SubmitReviewResponse,
    ReviewInfoForEmailResponse,
)


class ReviewImplementationRepository(ReviewRepository):
    """
    Implementación concreta de la interfaz ReviewRepository.
    Utiliza SQLAlchemy y el patrón de Unidad de Trabajo (Unit of Work) para interactuar
    con la base de datos PostgreSQL.
    """

    @property
    def _uow(self) -> UnitOfWork:
        """
        Propiedad privada para acceder de forma segura a la instancia actual de UnitOfWork.
        """
        try:
            return uow_var.get()
        except LookupError:
            raise RuntimeError(
                "UnitOfWork no encontrada en el contexto. "
                "Asegúrese de que el repositorio se usa dentro del alcance de una UnitOfWork."
            )

    async def process_appointment_for_review(
        self,
        appointment_id: int,
        days_after: int,
        user_transaction: str,
    ) -> ProcessAppointmentForReviewResponse:
        """
        Procesa una cita para verificar si debe enviarse email de review.
        Llama al procedimiento almacenado 'sp_process_appointment_for_review_email'.
        """
        sql_query = text(
            "SELECT * FROM sp_process_appointment_for_review_email(:appointment_id, :days_after, :user_transaction)"
        )

        params = {
            "appointment_id": appointment_id,
            "days_after": days_after,
            "user_transaction": user_transaction,
        }

        try:
            result = await self._uow.session.execute(sql_query, params)
            row = result.first()

            if not row:
                return ProcessAppointmentForReviewResponse(
                    success=False,
                    action="NOT_FOUND",
                    review_id=None,
                    token=None,
                    customer_email=None,
                    customer_name=None,
                    message="Cita no encontrada",
                    should_send_email=False,
                )

            return ProcessAppointmentForReviewResponse(
                success=row.success,
                action=row.action,
                review_id=row.review_id,
                token=row.token,
                customer_email=row.customer_email,
                customer_name=row.customer_name,
                message=row.message,
                should_send_email=row.should_send_email,
            )
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError(f"Error de base de datos al procesar cita para review: {e}")

    async def mark_email_sent(
        self,
        review_id: int,
        user_transaction: str,
    ) -> MarkEmailSentResponse:
        """
        Marca un review como email enviado.
        Llama al procedimiento almacenado 'sp_mark_review_email_sent'.
        """
        sql_query = text(
            "SELECT * FROM sp_mark_review_email_sent(:review_id, :user_transaction)"
        )

        params = {
            "review_id": review_id,
            "user_transaction": user_transaction,
        }

        try:
            result = await self._uow.session.execute(sql_query, params)
            row = result.first()

            if not row:
                return MarkEmailSentResponse(
                    success=False,
                    review_id=review_id,
                    email_sent_at=None,
                    message="Review no encontrado",
                )

            return MarkEmailSentResponse(
                success=row.success,
                review_id=row.review_id,
                email_sent_at=row.email_sent_at,
                message=row.message,
            )
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError(f"Error de base de datos al marcar email enviado: {e}")

    async def get_review_info_for_email(
        self,
        review_id: int,
    ) -> ReviewInfoForEmailResponse:
        """
        Obtiene la información del review necesaria para enviar el email.
        Llama al procedimiento almacenado 'sp_get_review_info_for_email'.
        """
        sql_query = text(
            "SELECT * FROM sp_get_review_info_for_email(:review_id)"
        )

        params = {
            "review_id": review_id,
        }

        try:
            result = await self._uow.session.execute(sql_query, params)
            row = result.first()

            if not row:
                return ReviewInfoForEmailResponse(
                    success=False,
                    review_id=review_id,
                    customer_email=None,
                    customer_name=None,
                    review_token=None,
                    service_name=None,
                    staff_name=None,
                    appointment_date=None,
                    location_name=None,
                    message="Review no encontrado",
                )

            return ReviewInfoForEmailResponse(
                success=row.success,
                review_id=row.review_id,
                customer_email=row.customer_email,
                customer_name=row.customer_name,
                review_token=row.review_token,
                service_name=row.service_name,
                staff_name=row.staff_name,
                appointment_date=row.appointment_date,
                location_name=row.location_name,
                message=row.message,
            )
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError(f"Error de base de datos al obtener info del review: {e}")

    async def validate_token(
        self,
        token: str,
    ) -> ValidateTokenResponse:
        """
        Valida un token de review y retorna información de la cita.
        Llama al procedimiento almacenado 'sp_validate_review_token'.
        """
        sql_query = text(
            "SELECT * FROM sp_validate_review_token(:token)"
        )

        params = {
            "token": token,
        }

        try:
            result = await self._uow.session.execute(sql_query, params)
            row = result.first()

            if not row:
                return ValidateTokenResponse(
                    valid=False,
                    review_id=None,
                    appointment_id=None,
                    customer_name=None,
                    service_name=None,
                    user_name=None,
                    start_datetime=None,
                    location_name=None,
                    already_reviewed=False,
                    token_expired=False,
                    message="Token no válido",
                )

            return ValidateTokenResponse(
                valid=row.valid,
                review_id=row.review_id,
                appointment_id=row.appointment_id,
                customer_name=row.customer_name,
                service_name=row.service_name,
                user_name=row.user_name,
                start_datetime=row.start_datetime,
                location_name=row.location_name,
                already_reviewed=row.already_reviewed,
                token_expired=row.token_expired,
                message=row.message,
            )
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError(f"Error de base de datos al validar token: {e}")

    async def submit_review(
        self,
        token: str,
        rating: int,
        comment: Optional[str],
        user_transaction: str,
    ) -> SubmitReviewResponse:
        """
        Guarda la calificación del cliente.
        Llama al procedimiento almacenado 'sp_submit_review'.
        """
        sql_query = text(
            "SELECT * FROM sp_submit_review(:token, :rating, :comment, :user_transaction)"
        )

        params = {
            "token": token,
            "rating": rating,
            "comment": comment,
            "user_transaction": user_transaction,
        }

        try:
            result = await self._uow.session.execute(sql_query, params)
            row = result.first()

            if not row:
                return SubmitReviewResponse(
                    success=False,
                    review_id=None,
                    message="Error al enviar review",
                )

            return SubmitReviewResponse(
                success=row.success,
                review_id=row.review_id,
                message=row.message,
            )
        except DBAPIError as e:
            handle_error(e)
            raise RuntimeError(f"Error de base de datos al enviar review: {e}")
