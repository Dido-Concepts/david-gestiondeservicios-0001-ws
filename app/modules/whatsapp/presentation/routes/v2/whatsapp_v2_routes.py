from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from mediatr import Mediator

# Importar el handler para forzar su registro
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)
from app.modules.whatsapp.application.commands.send_message.send_whatsapp_message_command_handler import (
    SendWhatsappMessageCommand,
)
from app.modules.whatsapp.application.request.send_whatsapp_message_request import (
    SendWhatsappMessageRequest,
)


class WhatsappV2Controller:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:

        self.router.post(
            "/whatsapp/send-message",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                200: {
                    "description": "Mensaje enviado exitosamente",
                    "content": {
                        "application/json": {
                            "example": {
                                "success": True,
                                "message": "Mensaje enviado correctamente",
                                "message_id": "msg_123456789",
                            }
                        }
                    },
                },
                400: {"description": "Error en los datos enviados"},
                500: {"description": "Error interno del servidor"},
            },
        )(self.send_whatsapp_message)

    async def send_whatsapp_message(
        self, request: SendWhatsappMessageRequest
    ) -> Dict[str, Any]:
        """
        Envía un mensaje de WhatsApp usando Evolution API
        """
        try:
            # Crear el comando usando MediatR
            command = SendWhatsappMessageCommand(
                number=request.number,
                text=request.text,
                delay=request.delay,
                linkPreview=request.linkPreview,
            )

            # Enviar el comando usando el mediador
            result: Dict[str, Any] = await self.mediator.send_async(command)

            if result.get("success"):
                return {
                    "success": True,
                    "message": "Mensaje enviado correctamente",
                    "data": result.get("data"),
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=result.get("message", "Error al enviar mensaje"),
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
