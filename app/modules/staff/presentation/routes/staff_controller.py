from typing import Any, Dict

from fastapi import APIRouter, Depends
from mediatr import Mediator

from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)


class StaffController:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.get(
            "/staff",
            dependencies=[Depends(permission_required(roles=["admin"]))],
            responses={
                200: {
                    "description": "Lista de staff",
                    "model": Dict[str, Any],
                }
            },
        )(self.get_staff)

    async def get_staff(self) -> Dict[str, Any]:
        """
        Obtiene una lista de staff (endpoint vacío por ahora)
        """
        # Endpoint vacío por el momento
        return {"message": "Staff endpoint - En desarrollo", "data": []}
