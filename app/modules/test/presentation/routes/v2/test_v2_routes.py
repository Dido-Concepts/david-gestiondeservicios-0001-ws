from typing import Any, Dict

from fastapi import APIRouter
from mediatr import Mediator


class TestController:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.get("/test")(self.get_test)
        self.router.get("/test/{test_id}")(self.get_test_by_id)

    async def get_test(self) -> Dict[str, str]:
        """
        Endpoint de prueba para la API v2
        """
        return {
            "message": "Hola desde la API v2!",
            "version": "2.0.0",
            "status": "active",
        }

    async def get_test_by_id(self, test_id: int) -> Dict[str, Any]:
        """
        Endpoint de prueba con parámetro para la API v2
        """
        return {
            "test_id": test_id,
            "message": f"Endpoint de prueba v2 con ID: {test_id}",
            "version": "2.0.0",
        }
