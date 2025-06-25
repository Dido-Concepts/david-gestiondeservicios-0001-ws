import math
from typing import Optional, Dict, Any, Literal
from mediatr import Mediator
from fastapi import Query
from pydantic import BaseModel, Field

from app.constants import injector_var
from app.modules.services.domain.entities.service_domain import ServiceEntity2
from app.modules.services.domain.repositories.service_repository import (
    ServiceRepository,
)

from app.modules.share.aplication.services.data_shaper_service import DataShaper
from app.modules.share.aplication.services.filter_parser_service import (
    FilterParserService,
)
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    MetaPaginatedItemsViewModel,
    PaginatedItemsViewModel,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class BaseFindServicesByLocationV2Query(BaseModel):
    page_index: int = Query(
        ge=1, description="Número de página (mínimo 1, requerido)", example=1
    )
    page_size: int = Query(
        ge=1, le=100, description="Tamaño de página (1-100, requerido)", example=10
    )
    order_by: Literal[
        "service_id",
        "service_name",
        "category_name",
        "price",
        "duration_minutes",
        "insert_date",
        "update_date",
    ] = Query(default="service_name", description="Campo por el cual ordenar")
    sort_by: Literal["ASC", "DESC"] = Query(
        default="ASC", description="Dirección del ordenamiento"
    )
    query: Optional[str] = Query(
        default=None, description="Texto para buscar en service_name o category_name"
    )

    fields: Optional[str] = Query(
        default=None,
        description="Campos a incluir separados por comas (ej: 'service_id,service_name,price')",
    )

    filters: Optional[str] = Query(
        default=None,
        description='Filtros en formato JSON: {"category_id": 1}',
        example='{"category_id": 1}',
    )


class ServiceFiltersModel(BaseModel):
    """Filtros específicos permitidos para servicios"""

    category_id: Optional[int] = Field(
        default=None, description="Filtrar por ID de categoría", ge=1
    )

    class Config:
        extra = "forbid"


class FindServicesByLocationV2Query(BaseFindServicesByLocationV2Query):
    """
    Modelo completo incluyendo table_name para el handler.
    """

    location_id: int = 0


@Mediator.handler
class FindServicesByLocationV2QueryHandler(
    IRequestHandler[
        FindServicesByLocationV2Query, PaginatedItemsViewModel[Dict[str, Any]]
    ]
):
    VALID_FIELDS = set(ServiceEntity2.__dataclass_fields__.keys())
    REQUIRED_FIELDS = {"service_id"}

    def __init__(self) -> None:
        injector = injector_var.get()
        self.service_repository = injector.get(ServiceRepository)  # type: ignore[type-abstract]
        self.data_shaper = DataShaper()
        self.filter_parser = FilterParserService()

    async def handle(
        self, query: FindServicesByLocationV2Query
    ) -> PaginatedItemsViewModel[Dict[str, Any]]:
        parsed_filters = self.filter_parser.parse_and_validate_filters(
            filters_json=query.filters, filter_model=ServiceFiltersModel
        )

        repo_result = await self.service_repository.find_services_by_location_v2(
            location_id=query.location_id,
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
