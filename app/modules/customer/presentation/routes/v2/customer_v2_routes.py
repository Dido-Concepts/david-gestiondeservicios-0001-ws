from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, Query
from mediatr import Mediator

from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)
from app.modules.customer.application.queries.get_customers_refactor.get_customers_refactor_handler import (
    FindCustomerRefactorQuery,
)
from app.modules.customer.domain.entities.customer_domain import CustomerEntity
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
)


class CustomerV2Controller:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.get(
            "/customer",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                200: {
                    "description": "Lista paginada de clientes",
                    "model": PaginatedItemsViewModel[CustomerEntity],
                }
            },
        )(self.get_customers)

    async def get_customers(
        self, query_params: Annotated[FindCustomerRefactorQuery, Query()]
    ) -> PaginatedItemsViewModel[Dict[str, Any]]:
        """
        Obtiene una lista paginada de clientes con filtros dinámicos
        """
        result: PaginatedItemsViewModel[
            Dict[str, Any]
        ] = await self.mediator.send_async(query_params)
        return result
