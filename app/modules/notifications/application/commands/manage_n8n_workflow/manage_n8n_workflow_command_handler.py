from os import getenv
from typing import Any, Dict

import httpx
from mediatr import Mediator
from pydantic import BaseModel

from app.modules.share.domain.handler.request_handler import IRequestHandler


class ManageN8nWorkflowCommand(BaseModel):
    """
    Comando para activar o desactivar el workflow de N8N
    """

    activate: bool  # True para activar, False para desactivar


@Mediator.handler
class ManageN8nWorkflowCommandHandler(
    IRequestHandler[ManageN8nWorkflowCommand, Dict[str, Any]]
):

    def __init__(self) -> None:
        # Variables de entorno para N8N
        self.n8n_url = getenv(
            "N8N_URL", "https://primary-production-fc447.up.railway.app"
        )
        self.n8n_api_key = getenv(
            "N8N_API_KEY",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMzJjNzQzMS0wZWU0LTQzMDYtYWMzZi0xYmZlZjQ5MjMzODUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxMTA2NDk5fQ.0O3sY0bskVlEWFtmiIoEI518wDcD6QSmQJOGPMMKsRw",
        )
        self.workflow_id = getenv("N8N_WORKFLOW_ID", "HHle98I8JYdDvXi3")

    async def handle(self, command: ManageN8nWorkflowCommand) -> Dict[str, Any]:
        """
        Activa o desactiva el workflow de N8N según el parámetro activate
        """
        try:
            action = "activate" if command.activate else "deactivate"
            url = f"{self.n8n_url}/api/v1/workflows/{self.workflow_id}/{action}"

            headers = {
                "X-N8N-API-KEY": self.n8n_api_key,
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers)

                if response.status_code == 200:
                    status = "active" if command.activate else "inactive"
                    action_text = "activado" if command.activate else "desactivado"

                    return {
                        "success": True,
                        "message": f"Workflow de N8N {action_text} exitosamente",
                        "workflow_id": self.workflow_id,
                        "status": status,
                        "action": action,
                    }
                else:
                    action_text = "activar" if command.activate else "desactivar"
                    return {
                        "success": False,
                        "message": f"Error al {action_text} el workflow: {response.text}",
                        "status_code": response.status_code,
                    }

        except Exception as e:
            action_text = "gestionar" if command.activate else "gestionar"
            return {
                "success": False,
                "message": f"Error interno al {action_text} el workflow: {str(e)}",
            }
