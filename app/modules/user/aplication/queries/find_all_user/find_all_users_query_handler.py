from datetime import datetime

from mediatr import Mediator
from pydantic import BaseModel, Field

from app.constants import injector_var
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    MetaPaginatedItemsViewModel,
    PaginatedItemsViewModel,
)
from app.modules.user.aplication.queries.find_all_role.find_all_role_query_handler import (
    FindAllRoleQueryResponse,
)
from app.modules.user.domain.models.user_enum import Status
from app.modules.user.domain.repositories.user_repository import UserRepository


class FindAllUsersRequest(BaseModel):
    page_index: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1)
    query: str = Field(None, min_length=1)


class FindAllUsersQuery:
    def __init__(self, request: FindAllUsersRequest):
        self.request = request


class FindAllUsersQueryResponse(BaseModel):
    id: int
    user_name: str
    email: str
    status: Status
    role: FindAllRoleQueryResponse
    created_at: datetime


@Mediator.handler
class FindAllUsersQueryHandler:
    def __init__(self) -> None:
        injector = injector_var.get()
        self.user_repository = injector.get(UserRepository)  # type: ignore[type-abstract]

    async def handle(
        self, query: FindAllUsersQuery
    ) -> PaginatedItemsViewModel[FindAllUsersQueryResponse]:
        res = await self.user_repository.find_users(
            page_index=query.request.page_index,
            page_size=query.request.page_size,
            query=query.request.query,
        )

        response_data = [
            FindAllUsersQueryResponse(
                id=user_role.user.id,
                user_name=user_role.user.user_name,
                email=user_role.user.email,
                status=user_role.user.status,
                role=FindAllRoleQueryResponse(
                    id=user_role.role.id,
                    description=user_role.role.description,
                    name=user_role.role.name,
                ),
                created_at=user_role.user.created_at,
            )
            for user_role in res.data
        ]

        meta = MetaPaginatedItemsViewModel(
            page=query.request.page_index,
            page_size=query.request.page_size,
            page_count=res.total_pages,
            total=res.total_items,
        )

        pagination = PaginatedItemsViewModel[FindAllUsersQueryResponse](
            data=response_data, meta=meta
        )

        return pagination
