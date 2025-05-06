from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.services.domain.repositories.category_repository import (
    CategoryRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class DeleteCategoryCommand(BaseModel):
    category_id: int
    user_delete: str


@Mediator.handler
class DeleteCategoryCommandHandler(IRequestHandler[DeleteCategoryCommand, bool]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.category_repository = injector.get(CategoryRepository)  # type: ignore[type-abstract]

    async def handle(self, command: DeleteCategoryCommand) -> bool:
        return await self.category_repository.delete_category(
            category_id=command.category_id,
            user_delete=command.user_delete,
        )
