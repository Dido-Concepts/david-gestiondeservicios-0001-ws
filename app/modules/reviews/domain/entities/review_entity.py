from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ProcessAppointmentForReviewResponse:
    """
    Entidad de respuesta para el procesamiento de una cita para review.
    Corresponde al resultado del SP 'sp_process_appointment_for_review_email'.
    """
    success: bool
    action: str
    review_id: Optional[int]
    token: Optional[str]
    customer_email: Optional[str]
    customer_name: Optional[str]
    message: str
    should_send_email: bool


@dataclass
class ReviewInfoForEmailResponse:
    """
    Entidad de respuesta para obtener información del review para enviar email.
    Corresponde al resultado del SP 'sp_get_review_info_for_email'.
    """
    success: bool
    review_id: int
    customer_email: Optional[str]
    customer_name: Optional[str]
    review_token: Optional[str]
    service_name: Optional[str]
    staff_name: Optional[str]
    appointment_date: Optional[datetime]
    location_name: Optional[str]
    message: str


@dataclass
class MarkEmailSentResponse:
    """
    Entidad de respuesta para marcar un review como email enviado.
    Corresponde al resultado del SP 'sp_mark_review_email_sent'.
    Incluye información del cliente y cita para enviar el email.
    """
    success: bool
    review_id: int
    email_sent_at: Optional[datetime]
    message: str
    # Información adicional para enviar el email
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    review_token: Optional[str] = None
    service_name: Optional[str] = None
    staff_name: Optional[str] = None
    appointment_date: Optional[datetime] = None
    location_name: Optional[str] = None


@dataclass
class ValidateTokenResponse:
    """
    Entidad de respuesta para la validación de un token de review.
    Corresponde al resultado del SP 'sp_validate_review_token'.
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


@dataclass
class SubmitReviewResponse:
    """
    Entidad de respuesta para el envío de una calificación.
    Corresponde al resultado del SP 'sp_submit_review'.
    """
    success: bool
    review_id: Optional[int]
    message: str


@dataclass
class ReviewResponse:
    review_id: int
    appointment_id: int
    token: str
    rating: Optional[int]
    comment: Optional[str]
    token_expires_at: datetime
    reviewed_at: Optional[datetime]
    email_sent_at: Optional[datetime]
    annulled: bool
    insert_date: datetime
    update_date: Optional[datetime]
    user_create: str
    user_modify: Optional[str]
