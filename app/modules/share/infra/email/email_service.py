import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

from config.setting import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_PORT_SSL,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
    SMTP_FROM_NAME,
    SMTP_USE_SSL,
    REVIEW_BASE_URL,
)


@dataclass
class EmailConfig:
    """Configuración del servidor SMTP."""
    smtp_host: str = SMTP_HOST
    smtp_port: int = SMTP_PORT
    smtp_port_ssl: int = SMTP_PORT_SSL
    username: str = SMTP_USERNAME
    password: str = SMTP_PASSWORD
    from_email: str = SMTP_FROM_EMAIL
    from_name: str = SMTP_FROM_NAME
    use_ssl: bool = SMTP_USE_SSL


@dataclass
class EmailMessage:
    """Mensaje de correo electrónico."""
    to_email: str
    subject: str
    body_html: str
    body_text: Optional[str] = None
    to_name: Optional[str] = None


@dataclass
class EmailResult:
    """Resultado del envío de correo."""
    success: bool
    message: str
    error: Optional[str] = None


class IEmailService(ABC):
    """Interfaz abstracta para el servicio de email."""
    
    @abstractmethod
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Envía un correo electrónico."""
        pass
    
    @abstractmethod
    async def send_review_email(
        self,
        to_email: str,
        to_name: str,
        review_token: str,
        customer_name: str,
    ) -> EmailResult:
        """Envía un correo de solicitud de review."""
        pass


class EmailService(IEmailService):
    """
    Servicio para envío de correos electrónicos usando SMTP.
    Configurado para usar mail.efsystemas.net
    """
    
    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig()
    
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """
        Envía un correo electrónico.
        
        Args:
            message: El mensaje a enviar.
            
        Returns:
            EmailResult con el resultado del envío.
        """
        try:
            # Crear mensaje MIME
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"] = f"{self.config.from_name} <{self.config.from_email}>"
            
            if message.to_name:
                msg["To"] = f"{message.to_name} <{message.to_email}>"
            else:
                msg["To"] = message.to_email
            
            # Agregar cuerpo de texto plano si existe
            if message.body_text:
                part_text = MIMEText(message.body_text, "plain", "utf-8")
                msg.attach(part_text)
            
            # Agregar cuerpo HTML
            part_html = MIMEText(message.body_html, "html", "utf-8")
            msg.attach(part_html)
            
            # Enviar correo
            if self.config.use_ssl:
                # Conexión SSL directa (puerto 465)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(
                    self.config.smtp_host,
                    self.config.smtp_port_ssl,
                    context=context
                ) as server:
                    server.login(self.config.username, self.config.password)
                    server.sendmail(
                        self.config.from_email,
                        message.to_email,
                        msg.as_string()
                    )
            else:
                # Conexión con STARTTLS (puerto 587)
                context = ssl.create_default_context()
                with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                    server.starttls(context=context)
                    server.login(self.config.username, self.config.password)
                    server.sendmail(
                        self.config.from_email,
                        message.to_email,
                        msg.as_string()
                    )
            
            return EmailResult(
                success=True,
                message=f"Correo enviado exitosamente a {message.to_email}"
            )
            
        except smtplib.SMTPAuthenticationError as e:
            return EmailResult(
                success=False,
                message="Error de autenticación SMTP",
                error=str(e)
            )
        except smtplib.SMTPException as e:
            return EmailResult(
                success=False,
                message="Error al enviar correo",
                error=str(e)
            )
        except Exception as e:
            return EmailResult(
                success=False,
                message="Error inesperado al enviar correo",
                error=str(e)
            )
    
    async def send_review_email(
        self,
        to_email: str,
        to_name: str,
        review_token: str,
        customer_name: str,
    ) -> EmailResult:
        """
        Envía un correo de solicitud de review al cliente.
        
        Args:
            to_email: Email del destinatario.
            to_name: Nombre del destinatario.
            review_token: Token único para el review.
            customer_name: Nombre del cliente para personalizar el mensaje.
            
        Returns:
            EmailResult con el resultado del envío.
        """
        # URL base para el review desde configuración
        review_url = f"{REVIEW_BASE_URL}?token={review_token}"
        
        subject = "¿Cómo fue tu experiencia? - Déjanos tu opinión"
        
        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">¡Gracias por tu visita!</h1>
            </div>

            <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px;">Hola <strong>{customer_name}</strong>,</p>

                <p style="font-size: 16px;">
                    Esperamos que hayas tenido una excelente experiencia con nuestro servicio.
                    Tu opinión es muy importante para nosotros y nos ayuda a mejorar continuamente.
                </p>

                <p style="font-size: 16px;">
                    ¿Podrías tomarte un momento para calificar tu experiencia?
                </p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{review_url}"
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                              color: white;
                              padding: 15px 40px;
                              text-decoration: none;
                              border-radius: 25px;
                              font-size: 18px;
                              font-weight: bold;
                              display: inline-block;">
                        Calificar mi experiencia
                    </a>
                </div>

                <p style="font-size: 14px; color: #666;">
                    Este enlace es único y personal. Por favor no lo compartas con nadie.
                </p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                <p style="font-size: 12px; color: #999; text-align: center;">
                    Si no solicitaste este correo o tienes alguna pregunta,
                    puedes ignorar este mensaje.
                </p>
            </div>
        </body>
        </html>
        """
        
        body_text = f"""
        ¡Gracias por tu visita!
        
        Hola {customer_name},
        
        Esperamos que hayas tenido una excelente experiencia con nuestro servicio.
        Tu opinión es muy importante para nosotros y nos ayuda a mejorar continuamente.
        
        ¿Podrías tomarte un momento para calificar tu experiencia?
        
        Visita este enlace: {review_url}
        
        Este enlace es único y personal. Por favor no lo compartas con nadie.
        
        Si no solicitaste este correo o tienes alguna pregunta, puedes ignorar este mensaje.
        """
        
        message = EmailMessage(
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            body_html=body_html,
            body_text=body_text
        )
        
        return await self.send_email(message)
