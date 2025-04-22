from fastapi import APIRouter, Depends
from mediatr import Mediator

from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import get_current_user, permission_required
from app.modules.services.application.commands.create_category.create_category_command_handler import CreateCategoryCommand
from app.modules.services.application.queries.get_categories.get_categories_handler import GetCategoriesQuery, GetCategoriesQueryResponse
from app.modules.services.application.request.create_category_request import CreateCategoryRequest


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

    async def create_category(
            self,
            request: CreateCategoryRequest,
            current_user: UserAuth = Depends(get_current_user)) -> int:

        if not current_user.email:
            raise ValueError("User email not found in token")

        command = CreateCategoryCommand(
            name_category=request.name_category,
            user_create=current_user.email,
            description_category=request.description_category
        )

        result: int = await self.mediator.send_async(command)
        return result

    async def get_categories(self) -> list[GetCategoriesQueryResponse]:
        query = GetCategoriesQuery()
        result: list[GetCategoriesQueryResponse] = await self.mediator.send_async(query)
        return result
