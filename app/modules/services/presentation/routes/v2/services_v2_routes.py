from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, Path, Query
from mediatr import Mediator

from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)
from app.modules.services.application.queries.get_services_by_location_v2.get_services_by_location_v2_handler import (
    BaseFindServicesByLocationV2Query,
    FindServicesByLocationV2Query,
)
from app.modules.services.domain.entities.service_domain import ServiceEntity2
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
)


class ServicesV2Controller:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.get(
            "/services/location/{location_id}",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                200: {
                    "description": "Lista paginada de servicios por ubicación",
                    "model": PaginatedItemsViewModel[ServiceEntity2],
                }
            },
        )(self.get_services_by_location)

    async def get_services_by_location(
        self,
        location_id: Annotated[
            int, Path(description="ID de la ubicación/sede", example=1)
        ],
        query_params: Annotated[BaseFindServicesByLocationV2Query, Query()],
    ) -> PaginatedItemsViewModel[Dict[str, Any]]:
        query_params = FindServicesByLocationV2Query(
            location_id=location_id, **query_params.model_dump()
        )

        result: PaginatedItemsViewModel[
            Dict[str, Any]
        ] = await self.mediator.send_async(query_params)
        return result
