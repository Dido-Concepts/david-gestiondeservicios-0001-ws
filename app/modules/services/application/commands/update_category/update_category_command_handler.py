from typing import Optional

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.services.domain.repositories.category_repository import (
    CategoryRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class UpdateCategoryCommand(BaseModel):
    category_id: int
    location_id: int
    name_category: str
    user_update: str
    description_category: Optional[str] = None


@Mediator.handler
class UpdateCategoryCommandHandler(IRequestHandler[UpdateCategoryCommand, str]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.category_repository = injector.get(CategoryRepository)  # type: ignore[type-abstract]

    async def handle(self, command: UpdateCategoryCommand) -> str:
        return await self.category_repository.update_category(
            category_id=command.category_id,
            sede_id=command.location_id,
            category_name=command.name_category,
            description=command.description_category,
            user_update=command.user_update,
        )
