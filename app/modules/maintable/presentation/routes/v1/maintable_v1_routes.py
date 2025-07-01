"""
Este módulo define las rutas del API para la versión 1 (v1) del recurso
de tablas de mantenimiento ('maintables'), utilizando un patrón de Controller
para agrupar la lógica de las rutas.
"""

# --- Importaciones Esenciales de FastAPI y Python ---
from typing import Annotated, Dict, Any
from fastapi import APIRouter, Depends, Path, Query
from mediatr import Mediator

# --- Importaciones de Autenticación/Autorización (replicando tu patrón) ---
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)

# --- Importaciones de la Lógica de Aplicación del Módulo ---
from app.modules.maintable.application.queries.get_by_criteria.get_by_criteria_query_handler import (
    BaseMaintableQuery,
    GetMaintableByCriteriaQuery,
)

# --- Importaciones de los ViewModels Compartidos ---
from app.modules.maintable.domain.entities.maintable_domain import MaintableEntity
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
)


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
            responses={
                "200": {
                    "model": PaginatedItemsViewModel[MaintableEntity],
                    "description": "Datos de la tabla obtenidos correctamente",
                }
            },
        )(self.get_maintable_data)

    async def get_maintable_data(
        self,
        # Usamos Annotated para ser explícitos sobre el origen de cada parámetro
        table_name: Annotated[
            str,
            Path(
                description="Nombre de la tabla a consultar.", example="maintable_user"
            ),
        ],
        query_params: Annotated[BaseMaintableQuery, Query()],
    ) -> PaginatedItemsViewModel[Dict[str, Any]]:
        query_params = GetMaintableByCriteriaQuery(
            table_name=table_name, **query_params.model_dump()
        )

        result: PaginatedItemsViewModel[
            Dict[str, Any]
        ] = await self.mediator.send_async(query_params)
        return result
