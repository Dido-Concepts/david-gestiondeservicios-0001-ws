from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, Query
from mediatr import Mediator

from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
)
from app.modules.staff.application.queries.get_staff_refactor.get_staff_refactor_handler import (
    FindStaffRefactorQuery,
)
from app.modules.staff.domain.entities.staff_domain import StaffEntity


class StaffV2Controller:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.get(
            "/staff",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                200: {
                    "description": "Lista paginada de miembros del staff",
                    "model": PaginatedItemsViewModel[StaffEntity],
                }
            },
        )(self.get_staff)

    async def get_staff(
        self, query_params: Annotated[FindStaffRefactorQuery, Query()]
    ) -> PaginatedItemsViewModel[Dict[str, Any]]:
        """
        Obtiene una lista paginada de miembros del staff con filtros dinámicos
        """
        result: PaginatedItemsViewModel[Dict[str, Any]] = (
            await self.mediator.send_async(query_params)
        )
        return result
