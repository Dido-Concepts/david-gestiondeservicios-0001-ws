from datetime import datetime
from typing import Optional

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class GetAllLocationsCatalogQuery(BaseModel):

    pass


class GetAllLocationsCatalogQueryResponse(BaseModel):
    id_sede: int
    nombre_sede: str
    telefono_sede: Optional[str]
    direccion_sede: Optional[str]
    insert_date: datetime
    file_id: Optional[int]
    review_location: str


@Mediator.handler
class FindAllLocationQueryHandler(
    IRequestHandler[
        GetAllLocationsCatalogQuery, list[GetAllLocationsCatalogQueryResponse]
    ]
):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.location_repository = injector.get(LocationRepository)  # type: ignore[type-abstract]

    async def handle(
        self, query: GetAllLocationsCatalogQuery
    ) -> list[GetAllLocationsCatalogQueryResponse]:

        res = await self.location_repository.get_all_location_catalog()

        response_data = [
            GetAllLocationsCatalogQueryResponse(
                id_sede=location.id,
                nombre_sede=location.nombre_sede,
                telefono_sede=location.telefono_sede,
                direccion_sede=location.direccion_sede,
                insert_date=location.insert_date,
                file_id=location.file_id,
                review_location=location.review_location,
            )
            for location in res
        ]
        return response_data
