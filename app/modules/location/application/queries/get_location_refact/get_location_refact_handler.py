import math
from typing import Optional, Dict, Any, Literal
from mediatr import Mediator
from fastapi import Query
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.location.domain.entities.location_domain import LocationEntity
from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)

from app.modules.share.aplication.services.data_shaper_service import DataShaper
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    MetaPaginatedItemsViewModel,
    PaginatedItemsViewModel,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class FindLocationRefactorQuery(BaseModel):
    page_index: int = Query(
        ge=1, description="Número de página (mínimo 1, requerido)", example=1
    )
    page_size: int = Query(
        ge=1, le=100, description="Tamaño de página (1-100, requerido)", example=10
    )
    order_by: Literal[
        "id",
        "nombre_sede",
        "telefono_sede",
        "direccion_sede",
        "insert_date",
        "update_date",
        "status",
    ] = Query(default="id", description="Campo por el cual ordenar")
    sort_by: Literal["ASC", "DESC"] = Query(
        default="ASC", description="Dirección del ordenamiento"
    )
    query: Optional[str] = Query(
        default=None, description="Texto para buscar en nombre_sede"
    )
    fields: Optional[str] = Query(
        default=None,
        description="Campos a incluir separados por comas (ej: 'id,nombre_sede,telefono_sede')",
    )


@Mediator.handler
class FindAllLocationQueryHandler(
    IRequestHandler[FindLocationRefactorQuery, PaginatedItemsViewModel[Dict[str, Any]]]
):
    VALID_FIELDS = set(LocationEntity.__dataclass_fields__.keys())
    REQUIRED_FIELDS = {"id"}

    def __init__(self) -> None:
        injector = injector_var.get()
        self.location_repository = injector.get(LocationRepository)  # type: ignore[type-abstract]
        self.data_shaper = DataShaper()

    async def handle(
        self, query: FindLocationRefactorQuery
    ) -> PaginatedItemsViewModel[Dict[str, Any]]:
        repo_result = await self.location_repository.find_location_refactor(
            page_index=query.page_index,
            page_size=query.page_size,
            order_by=query.order_by,
            sort_by=query.sort_by,
            query=query.query,
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

        # 4. Construir respuesta paginada
        pagination = PaginatedItemsViewModel[Dict[str, Any]](
            data=shaped_data, meta=meta
        )

        return pagination
