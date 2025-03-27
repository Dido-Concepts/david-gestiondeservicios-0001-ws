from datetime import datetime
from typing import Optional

from mediatr import Mediator
from pydantic import BaseModel, Field

from app.constants import injector_var
from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    MetaPaginatedItemsViewModel,
    PaginatedItemsViewModel,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class FindAllLocationQuery(BaseModel):
    page_index: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1)


class FindAllLocationQueryResponse(BaseModel):
    id: int
    name_location: str
    phone_location: str
    address_location: str
    location_review: str
    insert_date: datetime
    annulled: bool
    url: Optional[str] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None


@Mediator.handler
class FindAllLocationQueryHandler(
    IRequestHandler[
        FindAllLocationQuery, PaginatedItemsViewModel[FindAllLocationQueryResponse]
    ]
):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.location_repository = injector.get(LocationRepository)  # type: ignore[type-abstract]

    async def handle(
        self, query: FindAllLocationQuery
    ) -> PaginatedItemsViewModel[FindAllLocationQueryResponse]:

        res = await self.location_repository.find_locations(
            page_index=query.page_index,
            page_size=query.page_size,
        )

        response_data = [
            FindAllLocationQueryResponse(
                id=location.id,
                name_location=location.nombre_sede,
                phone_location=location.telefono_sede,
                address_location=location.direccion_sede,
                insert_date=location.insert_date,
                location_review=location.location_review,
                url=location.url,
                annulled=location.annulled,
                filename=location.filename,
                content_type=location.content_type,
                size=location.size,
            )
            for location in res.data
        ]

        meta = MetaPaginatedItemsViewModel(
            page=query.page_index,
            page_size=query.page_size,
            page_count=res.total_pages,
            total=res.total_items,
        )

        pagination = PaginatedItemsViewModel[FindAllLocationQueryResponse](
            data=response_data, meta=meta
        )

        return pagination
