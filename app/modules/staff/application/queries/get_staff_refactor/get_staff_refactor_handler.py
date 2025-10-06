import math
from typing import Any, Dict, Literal, Optional

from fastapi import Query
from mediatr import Mediator
from pydantic import BaseModel, Field

from app.constants import injector_var
from app.modules.share.aplication.services.data_shaper_service import DataShaper
from app.modules.share.aplication.services.filter_parser_service import (
    FilterParserService,
)
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    MetaPaginatedItemsViewModel,
    PaginatedItemsViewModel,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.staff.domain.entities.staff_domain import StaffEntity
from app.modules.staff.domain.repositories.staff_repository import StaffRepository


class FindStaffRefactorQuery(BaseModel):
    page_index: int = Query(
        ge=1, description="Número de página (mínimo 1, requerido)", example=1
    )
    page_size: int = Query(
        ge=1, le=100, description="Tamaño de página (1-100, requerido)", example=10
    )
    order_by: Literal[
        "id",
        "user_name",
        "email",
        "status",
        "location_id",
        "location_name",
        "created_at",
        "updated_at",
    ] = Query(default="id", description="Campo por el cual ordenar")
    sort_by: Literal["ASC", "DESC"] = Query(
        default="ASC", description="Dirección del ordenamiento"
    )
    query: Optional[str] = Query(
        default=None, description="Texto para buscar en user_name o email"
    )

    fields: Optional[str] = Query(
        default=None,
        description="Campos a incluir separados por comas (ej: 'id,user_name,email')",
    )

    filters: Optional[str] = Query(
        default=None,
        description='Filtros en formato JSON: {"role_id": 7, "location_id": 4} Permite filtrar por role_id y location_id únicamente',
        example='{"role_id": 7, "location_id": 4}',
    )


class StaffFiltersModel(BaseModel):
    """Filtros específicos permitidos para staff"""

    location_id: Optional[int] = Field(
        default=None,
        description="Filtrar por ID de ubicación",
    )

    role_id: Optional[int] = Field(
        default=None,
        description="Filtrar por ID de rol",
    )

    class Config:
        extra = "forbid"


@Mediator.handler
class FindAllStaffQueryHandler(
    IRequestHandler[FindStaffRefactorQuery, PaginatedItemsViewModel[Dict[str, Any]]]
):
    VALID_FIELDS = set(StaffEntity.__dataclass_fields__.keys())
    REQUIRED_FIELDS = {"id"}

    def __init__(self) -> None:
        injector = injector_var.get()
        self.staff_repository = injector.get(StaffRepository)  # type: ignore[type-abstract]
        self.data_shaper = DataShaper()
        self.filter_parser = FilterParserService()

    async def handle(
        self, query: FindStaffRefactorQuery
    ) -> PaginatedItemsViewModel[Dict[str, Any]]:
        parsed_filters = self.filter_parser.parse_and_validate_filters(
            filters_json=query.filters, filter_model=StaffFiltersModel
        )

        repo_result = await self.staff_repository.find_staff_refactor(
            page_index=query.page_index,
            page_size=query.page_size,
            order_by=query.order_by,
            sort_by=query.sort_by,
            query=query.query,
            filters=parsed_filters,
        )

        total_count = repo_result.total_items

        shaped_data = self.data_shaper.shape_data(
            data=repo_result.data,
            fields=query.fields,
            allowed_fields=self.VALID_FIELDS,
            required_fields=self.REQUIRED_FIELDS,
        )

        total_pages = math.ceil(total_count / query.page_size)

        meta = MetaPaginatedItemsViewModel(
            page=query.page_index,
            page_size=query.page_size,
            page_count=total_pages,
            total=total_count,
        )

        pagination = PaginatedItemsViewModel[Dict[str, Any]](
            data=shaped_data, meta=meta
        )

        return pagination
