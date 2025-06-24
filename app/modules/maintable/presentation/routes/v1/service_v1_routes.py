from typing import Annotated

from fastapi import APIRouter, Depends, Path
from mediatr import Mediator

from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_current_user,
    permission_required,
)
from app.modules.services.application.commands.create_service.create_service_command_handler import (
    CreateServiceCommand,
)
from app.modules.services.application.commands.delete_service.delete_service_command_handler import (
    DeleteServiceCommand,
)
from app.modules.services.application.commands.update_service.update_service_command_handler import (
    UpdateServiceCommand,
)
from app.modules.services.application.request.create_service_request import (
    CreateServiceRequest,
)
from app.modules.services.application.request.update_service_request import (
    UpdateServiceRequest,
)


class ServiceController:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.post(
            "/service",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.create_service)

        self.router.put(
            "/service/{service_id}",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.update_service)

        self.router.delete(
            "/service/{service_id}",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.delete_service)

    async def create_service(
        self,
        request: CreateServiceRequest,
        current_user: UserAuth = Depends(get_current_user),
    ) -> str:
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = CreateServiceCommand(
            service_name=request.service_name,
            category_id=request.category_id,
            price=request.price,
            duration=request.duration,
            user_create=current_user.email,
            description=request.description,
        )

        result: str = await self.mediator.send_async(command)
        return result

    async def update_service(
        self,
        service_id: Annotated[int, Path()],
        request: UpdateServiceRequest,
        current_user: UserAuth = Depends(get_current_user),
    ) -> str:
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = UpdateServiceCommand(
            service_id=service_id,
            service_name=request.service_name,
            category_id=request.category_id,
            price=request.price,
            duration=request.duration,
            user_update=current_user.email,
            description=request.description,
        )

        result: str = await self.mediator.send_async(command)
        return result

    async def delete_service(
        self,
        service_id: Annotated[int, Path()],
        current_user: UserAuth = Depends(get_current_user),
    ) -> bool:
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = DeleteServiceCommand(
            service_id=service_id,
            user_delete=current_user.email,
        )

        result: bool = await self.mediator.send_async(command)
        return result
