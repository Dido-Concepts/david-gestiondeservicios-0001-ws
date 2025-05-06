from typing import Optional

from mediatr import Mediator
from pydantic import BaseModel, Field

from app.constants import injector_var
from app.modules.services.domain.repositories.service_repository import (
    ServiceRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class UpdateServiceCommand(BaseModel):
    service_id: int
    service_name: str = Field(..., max_length=150)
    category_id: int
    price: float = Field(..., ge=0, le=9999999.99)
    duration: float = Field(..., ge=0, le=999.9)
    user_update: str = Field(..., max_length=50)
    description: Optional[str] = None


@Mediator.handler
class UpdateServiceCommandHandler(IRequestHandler[UpdateServiceCommand, str]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.service_repository = injector.get(ServiceRepository)  # type: ignore[type-abstract]

    async def handle(self, command: UpdateServiceCommand) -> str:
        return await self.service_repository.update_service(
            service_id=command.service_id,
            service_name=command.service_name,
            description=command.description,
            category_id=command.category_id,
            price=command.price,
            duration=command.duration,
            user_update=command.user_update,
        )
