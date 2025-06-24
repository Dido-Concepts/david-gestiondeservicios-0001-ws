from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.services.domain.repositories.service_repository import (
    ServiceRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler


class DeleteServiceCommand(BaseModel):
    service_id: int
    user_delete: str


@Mediator.handler
class DeleteServiceCommandHandler(IRequestHandler[DeleteServiceCommand, bool]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.service_repository = injector.get(ServiceRepository)  # type: ignore[type-abstract]

    async def handle(self, command: DeleteServiceCommand) -> bool:
        return await self.service_repository.delete_service(
            service_id=command.service_id,
            user_delete=command.user_delete,
        )
