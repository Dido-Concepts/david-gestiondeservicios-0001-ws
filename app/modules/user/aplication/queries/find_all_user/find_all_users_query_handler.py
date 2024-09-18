from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.user.domain.models.user_domain import User
from app.modules.user.domain.repositories.user_repository import UserRepository
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
    MetaPaginatedItemsViewModel,
)
from app.modules.user.aplication.queries.find_all_user.find_all_users_query import (
    FindAllUsersQuery,
)


class FindAllUsersQueryHandler(
    IRequestHandler[FindAllUsersQuery, PaginatedItemsViewModel[User]]
):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def handle(self, query: FindAllUsersQuery) -> PaginatedItemsViewModel[User]:
        res = await self.user_repository.find_all_users(
            page_index=query.page_index, page_size=query.page_size
        )

        meta = MetaPaginatedItemsViewModel(
            page=query.page_index,
            page_size=query.page_size,
            page_count=res.total_pages,
            total=res.total_items,
        )

        pagination = PaginatedItemsViewModel[User](data=res.data, meta=meta)

        return pagination
