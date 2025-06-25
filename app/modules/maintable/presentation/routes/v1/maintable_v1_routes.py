"""
Este módulo define las rutas del API para la versión 1 (v1) del recurso
de tablas de mantenimiento ('maintables'), utilizando un patrón de Controller
para agrupar la lógica de las rutas.
"""

# --- Importaciones Esenciales de FastAPI y Python ---
from typing import Optional, Annotated, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, Request, HTTPException, status
from mediatr import Mediator
from pydantic import BaseModel, Field # <--- ¡LÍNEA AÑADIDA PARA CORREGIR EL ERROR!

# --- Importaciones de Autenticación/Autorización (replicando tu patrón) ---
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)

# --- Importaciones de la Lógica de Aplicación del Módulo ---
from app.modules.maintable.application.queries.get_by_criteria.get_by_criteria_query_handler import (
    GetMaintableByCriteriaQuery
)

# --- Importaciones de los ViewModels Compartidos ---
from app.modules.share.aplication.view_models.paginated_items_view_model import PaginatedItemsViewModel


# --- Definición del Controlador ---
class MaintableController:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        """Define y añade la ruta de listado genérico al router."""
        self.router.get(
            "/maintable/{table_name}",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            openapi_extra={
                "responses": {
                    "200": {
                        "description": "Lista paginada de elementos de tabla de mantenimiento con campos dinámicos",
                        "content": {
                            "application/json": {
                                "example": {
                                    "data": [
                                        {
                                            "maintable_id": 1,
                                            "item_text": "Categoría Ejemplo 1",
                                            "item_value": "categoria_1",
                                            "item_order": 1,
                                            "description": "Descripción de categoría ejemplo 1",
                                            "insert_date": "2024-01-01T12:00:00.000000",
                                            "update_date": "2024-01-02T14:30:00.000000",
                                            "user_create": "admin@sistema.com",
                                            "user_modify": "admin@sistema.com",
                                            "status": True,
                                        },
                                        {
                                            "maintable_id": 2,
                                            "item_text": "Categoría Ejemplo 2",
                                            "item_value": "categoria_2",
                                            "item_order": 2,
                                            "description": "Descripción de categoría ejemplo 2",
                                            "insert_date": "2024-01-01T12:00:00.000000",
                                            "update_date": None,
                                            "user_create": "admin@sistema.com",
                                            "user_modify": None,
                                            "status": True,
                                        },
                                        {
                                            "maintable_id": 3,
                                            "item_text": "Servicio Ejemplo 1",
                                            "item_value": "servicio_1",
                                            "item_order": 1,
                                            "description": "Descripción de servicio ejemplo 1",
                                            "insert_date": "2024-01-01T12:00:00.000000",
                                            "update_date": "2024-01-03T10:15:00.000000",
                                            "user_create": "admin@sistema.com",
                                            "user_modify": "staff@sistema.com",
                                            "status": False,
                                        },
                                    ],
                                    "meta": {
                                        "page": 1,
                                        "page_size": 10,
                                        "page_count": 1,
                                        "total": 3,
                                    },
                                }
                            }
                        },
                    }
                }
            },
        )(self.get_maintable_data)

    async def get_maintable_data(
        self,
        # Usamos Annotated para ser explícitos sobre el origen de cada parámetro
        table_name: Annotated[str, Path(description="Nombre de la tabla a consultar.")],
        query_params: GetMaintableByCriteriaQuery = Depends()
    ) -> PaginatedItemsViewModel[Dict[str, Any]]:
        
        query_params.table_name = table_name

        result: PaginatedItemsViewModel[
            Dict[str, Any]
        ] = await self.mediator.send_async(query_params)
        return result