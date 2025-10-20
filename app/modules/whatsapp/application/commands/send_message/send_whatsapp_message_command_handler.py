from typing import Any, Dict, Optional

from mediatr import Mediator
from pydantic import BaseModel

from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.whatsapp.infra.services.evolution_api_service import (
    EvolutionApiService,
)


# --- Definición del Comando ---
class SendWhatsappMessageCommand(BaseModel):
    """
    Comando para solicitar el envío de un mensaje de WhatsApp.
    Utiliza Pydantic para validar los datos de entrada.
    """

    number: str
    text: str
    delay: Optional[int] = None
    linkPreview: Optional[bool] = True


# --- Definición del Manejador del Comando ---
@Mediator.handler
class SendWhatsappMessageCommandHandler(
    IRequestHandler[SendWhatsappMessageCommand, Dict[str, Any]]
):
    """
    Manejador para el comando SendWhatsappMessageCommand.
    Orquesta el envío de mensajes de WhatsApp utilizando Evolution API.
    """

    def __init__(self) -> None:
        """
        Constructor: Inicializa el servicio de Evolution API.
        """
        self.evolution_service = EvolutionApiService()

    async def handle(self, command: SendWhatsappMessageCommand) -> Dict[str, Any]:
        """
        Lógica para manejar el comando SendWhatsappMessageCommand.

        Args:
            command: El objeto comando con los datos del mensaje a enviar.

        Returns:
            Respuesta de Evolution API con los detalles del mensaje enviado.

        Raises:
            Exception: Si ocurre un error al enviar el mensaje.
        """
        try:
            # Delega el envío del mensaje al servicio de Evolution API
            response = await self.evolution_service.send_text_message(
                number=command.number,
                text=command.text,
                delay=command.delay,
                link_preview=command.linkPreview,
            )

            return {
                "success": True,
                "message": "Mensaje enviado correctamente",
                "data": response,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error al enviar mensaje: {str(e)}",
                "data": None,
            }
