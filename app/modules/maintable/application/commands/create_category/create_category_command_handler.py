from typing import Optional

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.services.domain.repositories.category_repository import (
    CategoryRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class CreateCategoryCommand(BaseModel):
    location_id: int
    name_category: str
    user_create: str
    description_category: Optional[str] = None


@Mediator.handler
class CreateCategoryCommandHandler(IRequestHandler[CreateCategoryCommand, str]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.location_repository = injector.get(CategoryRepository)  # type: ignore[type-abstract]

    async def handle(self, command: CreateCategoryCommand) -> str:

        return await self.location_repository.create_category(
            sede_id=command.location_id,
            category_name=command.name_category,
            description=command.description_category,
            user_create=command.user_create,
        )
