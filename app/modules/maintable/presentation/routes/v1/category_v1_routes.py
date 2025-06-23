from typing import Annotated

from fastapi import APIRouter, Depends, Query, Path
from mediatr import Mediator

from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_current_user,
    permission_required,
)
from app.modules.services.application.commands.create_category.create_category_command_handler import (
    CreateCategoryCommand,
)
from app.modules.services.application.commands.delete_category.delete_category_command_handler import (
    DeleteCategoryCommand,
)
from app.modules.services.application.commands.update_category.update_category_command_handler import (
    UpdateCategoryCommand,
)
from app.modules.services.application.queries.get_categories.get_categories_handler import (
    GetCategoriesQuery,
    GetCategoriesQueryResponse,
)
from app.modules.services.application.request.create_category_request import (
    CreateCategoryRequest,
)
from app.modules.services.application.request.update_category_request import (
    UpdateCategoryRequest,
)
from app.modules.services.application.queries.get_all_categories_catalog.get_all_categories_catalog_handler import (
    GetAllCategoriesCatalogQuery,
    GetAllCategoriesCatalogQueryResponse,
)


class CategoryController:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.post(
            "/category",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.create_category)

        self.router.get(
            "/category",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.get_categories)

        self.router.put(
            "/category/{category_id}",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.update_category)

        self.router.delete(
            "/category/{category_id}",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.delete_category)

        self.router.get(
            "/category/catalog/{sede_id}",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.get_all_categories_catalog)

    async def create_category(
        self,
        request: CreateCategoryRequest,
        current_user: UserAuth = Depends(get_current_user),
    ) -> str:
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = CreateCategoryCommand(
            location_id=request.location_id,
            name_category=request.name_category,
            user_create=current_user.email,
            description_category=request.description_category,
        )

        result: str = await self.mediator.send_async(command)
        return result

    async def get_categories(
        self, query: Annotated[GetCategoriesQuery, Query()]
    ) -> list[GetCategoriesQueryResponse]:
        result: list[GetCategoriesQueryResponse] = await self.mediator.send_async(query)
        return result

    async def update_category(
        self,
        category_id: Annotated[int, Path()],
        request: UpdateCategoryRequest,
        current_user: UserAuth = Depends(get_current_user),
    ) -> str:
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = UpdateCategoryCommand(
            category_id=category_id,
            location_id=request.location_id,
            name_category=request.name_category,
            user_update=current_user.email,
            description_category=request.description_category,
        )

        result: str = await self.mediator.send_async(command)
        return result

    async def delete_category(
        self,
        category_id: Annotated[int, Path()],
        current_user: UserAuth = Depends(get_current_user),
    ) -> bool:
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = DeleteCategoryCommand(
            category_id=category_id,
            user_delete=current_user.email,
        )

        result: bool = await self.mediator.send_async(command)
        return result

    async def get_all_categories_catalog(
        self,
        sede_id: Annotated[int, Path()],
    ) -> list[GetAllCategoriesCatalogQueryResponse]:
        query = GetAllCategoriesCatalogQuery(sede_id=sede_id)
        result: list[
            GetAllCategoriesCatalogQueryResponse
        ] = await self.mediator.send_async(query)
        return result
