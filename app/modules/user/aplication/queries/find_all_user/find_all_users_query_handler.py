from app.modules.share.aplication.view_models.paginated_items_view_model import (
    MetaPaginatedItemsViewModel,
    PaginatedItemsViewModel,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.user.aplication.queries.find_all_role.find_all_role_query_response import (
    FindAllRoleQueryResponse,
)
from app.modules.user.aplication.queries.find_all_user.find_all_users_query import (
    FindAllUsersQuery,
)
from app.modules.user.aplication.queries.find_all_user.find_all_users_query_response import (
    FindAllUsersQueryResponse,
)
from app.modules.user.domain.repositories.user_repository import UserRepository


class FindAllUsersQueryHandler(
    IRequestHandler[
        FindAllUsersQuery, PaginatedItemsViewModel[FindAllUsersQueryResponse]
    ]
):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def handle(
        self, query: FindAllUsersQuery
    ) -> PaginatedItemsViewModel[FindAllUsersQueryResponse]:
        res = await self.user_repository.find_users(
            page_index=query.page_index, page_size=query.page_size, query=query.query
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
            page=query.page_index,
            page_size=query.page_size,
            page_count=res.total_pages,
            total=res.total_items,
        )

        pagination = PaginatedItemsViewModel[FindAllUsersQueryResponse](
            data=response_data, meta=meta
        )

        return pagination
