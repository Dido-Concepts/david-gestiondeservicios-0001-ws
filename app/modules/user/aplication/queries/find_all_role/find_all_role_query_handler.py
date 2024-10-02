from typing import List

from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.user.aplication.queries.find_all_role.find_all_role_query_response import (
    FindAllRoleQueryResponse,
)
from app.modules.user.domain.repositories.role_repository import RoleRepository


class FindAllRoleHandler(IRequestHandler[None, List[FindAllRoleQueryResponse]]):
    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    async def handle(self, query: None) -> List[FindAllRoleQueryResponse]:
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
