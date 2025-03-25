import json
from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile
from mediatr import Mediator

from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_current_user,
    permission_required,
)
from app.modules.location.application.commands.create_location.create_location_command_handler import (
    CreateLocationCommand,
)


class LocationController:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.post(
            "/location",
            dependencies=[Depends(permission_required(roles=["admin"]))],
            openapi_extra={
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name_location": {
                                        "type": "string",
                                        "example": "Mi Ubicacion 123",
                                    },
                                    "phone": {"type": "string", "example": "942404311"},
                                    "address": {
                                        "type": "string",
                                        "example": "Calle Principal 123 #45",
                                    },
                                    "schedule": {
                                        "type": "string",
                                        "example": json.dumps(
                                            [
                                                {
                                                    "day": "Lunes",
                                                    "start_time": "09:00",
                                                    "end_time": "10:00",
                                                },
                                                {
                                                    "day": "Martes",
                                                    "start_time": "10:00",
                                                    "end_time": "11:00",
                                                },
                                            ]
                                        ),
                                    },
                                    "img_file": {
                                        "type": "string",
                                        "format": "binary",
                                        "example": "Archivo de imagen (ej. imagen.jpg)",
                                    },
                                },
                            }
                        }
                    }
                }
            },
        )(self.create_location)

    async def create_location(
        self,
        name_location: Annotated[str, Form()],
        phone: Annotated[str, Form()],
        address: Annotated[str, Form()],
        img_file: UploadFile,
        schedule: Annotated[str, Form()],
        current_user: UserAuth = Depends(get_current_user),
    ) -> int:

        if not current_user.email:
            raise ValueError("User email not found in token")

        command = CreateLocationCommand(
            name_location=name_location,
            phone=phone,
            address=address,
            img_file=img_file,
            schedule=schedule,
            user_create=current_user.email,
        )

        result: int = await self.mediator.send_async(command)
        return result
