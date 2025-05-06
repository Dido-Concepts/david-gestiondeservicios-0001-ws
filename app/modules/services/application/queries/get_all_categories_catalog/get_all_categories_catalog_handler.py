from datetime import datetime
from typing import Optional

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.services.domain.repositories.category_repository import (
    CategoryRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class GetAllCategoriesCatalogQuery(BaseModel):
    sede_id: int
    pass


class GetAllCategoriesCatalogQueryResponse(BaseModel):
    category_id: int
    sede_id: int
    category_name: str
    description: Optional[str]
    created_at: datetime


@Mediator.handler
class GetAllCategoriesCatalogQueryHandler(
    IRequestHandler[
        GetAllCategoriesCatalogQuery, list[GetAllCategoriesCatalogQueryResponse]
    ]
):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.category_repository = injector.get(CategoryRepository)  # type: ignore[type-abstract]

    async def handle(
        self, query: GetAllCategoriesCatalogQuery
    ) -> list[GetAllCategoriesCatalogQueryResponse]:
        res = await self.category_repository.get_all_categories_catalog(
            sede_id=query.sede_id
        )

        response_data = [
            GetAllCategoriesCatalogQueryResponse(
                category_id=category.category_id,
                sede_id=category.sede_id,
                category_name=category.category_name,
                description=category.description,
                created_at=category.insert_date,
            )
            for category in res
        ]
        return response_data
