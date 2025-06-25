from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, Query
from mediatr import Mediator

from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)
from app.modules.location.application.queries.get_location_refact.get_location_refact_handler import (
    FindLocationRefactorQuery,
)
from app.modules.location.domain.entities.location_domain import LocationEntity
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
)


class LocationV2Controller:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.get(
            "/location",
            dependencies=[Depends(permission_required(roles=["admin"]))],
            responses={
                200: {
                    "description": "Lista paginada de ubicaciones",
                    "model": PaginatedItemsViewModel[LocationEntity],
                }
            },
        )(self.get_locations)

    async def get_locations(
        self, query_params: Annotated[FindLocationRefactorQuery, Query()]
    ) -> PaginatedItemsViewModel[Dict[str, Any]]:
        """
        Obtiene una lista paginada de ubicaciones con filtros dinámicos
        """
        result: PaginatedItemsViewModel[
            Dict[str, Any]
        ] = await self.mediator.send_async(query_params)
        return result
