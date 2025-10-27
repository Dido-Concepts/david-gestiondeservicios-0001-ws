from os import getenv
from typing import Any, Dict

import httpx
from mediatr import Mediator
from pydantic import BaseModel

from app.modules.share.domain.handler.request_handler import IRequestHandler


class GetN8nWorkflowStatusQuery(BaseModel):
    """
    Query para obtener el estado actual del workflow de N8N
    """

    pass


@Mediator.handler
class GetN8nWorkflowStatusQueryHandler(
    IRequestHandler[GetN8nWorkflowStatusQuery, Dict[str, Any]]
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

    async def handle(self, query: GetN8nWorkflowStatusQuery) -> Dict[str, Any]:
        """
        Obtiene el estado actual del workflow de N8N
        """
        try:
            url = f"{self.n8n_url}/api/v1/workflows/{self.workflow_id}"

            headers = {
                "X-N8N-API-KEY": self.n8n_api_key,
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    workflow_data = response.json()
                    is_active = workflow_data.get("active", False)

                    return {
                        "success": True,
                        "workflow_id": self.workflow_id,
                        "is_active": is_active,
                        "status": "active" if is_active else "inactive",
                        "workflow_name": workflow_data.get("name", "Unknown"),
                        "last_updated": workflow_data.get("updatedAt"),
                        "created_at": workflow_data.get("createdAt"),
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Error al consultar el estado del workflow: {response.text}",
                        "status_code": response.status_code,
                        "workflow_id": self.workflow_id,
                    }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error interno al consultar el estado del workflow: {str(e)}",
                "workflow_id": self.workflow_id,
            }
