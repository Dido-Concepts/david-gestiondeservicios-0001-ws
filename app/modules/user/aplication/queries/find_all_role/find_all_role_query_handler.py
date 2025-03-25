from typing import List

from mediatr import Mediator
from pydantic import BaseModel

from app.constants import injector_var
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.user.domain.repositories.role_repository import RoleRepository


class FindAllRoleQuery(BaseModel):
    pass


class FindAllRoleQueryResponse(BaseModel):
    id: int
    name: str
    description: str


@Mediator.handler
class FindAllRoleHandler(
    IRequestHandler[FindAllRoleQuery, List[FindAllRoleQueryResponse]]
):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.role_repository = injector.get(RoleRepository)  # type: ignore[type-abstract]

    async def handle(self, query: FindAllRoleQuery) -> List[FindAllRoleQueryResponse]:
        res = await self.role_repository.find_all()

        response_data = [
            FindAllRoleQueryResponse(
                id=role.id,
                name=role.name,
                description=role.description,
            )
            for role in res
        ]

        return response_data
