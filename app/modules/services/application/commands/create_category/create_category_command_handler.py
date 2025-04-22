from typing import Optional
from mediatr import Mediator
from pydantic import BaseModel

from app.modules.services.domain.repositories.category_repository import (
    CategoryRepository,
)

from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.constants import injector_var


class CreateCategoryCommand(BaseModel):
    name_category: str
    user_create: str
    description_category: Optional[str] = None


@Mediator.handler
class CreateCategoryCommandHandler(IRequestHandler[CreateCategoryCommand, int]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.location_repository = injector.get(CategoryRepository)  # type: ignore[type-abstract]

    async def handle(self, command: CreateCategoryCommand) -> int:

        return await self.location_repository.create_category(
            name_category=command.name_category,
            user_create=command.user_create,
            description_category=command.description_category,
        )
