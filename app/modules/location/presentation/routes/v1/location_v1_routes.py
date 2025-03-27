import json
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, Path, Query, UploadFile
from mediatr import Mediator

from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_current_user,
    permission_required,
)
from app.modules.location.application.commands.create_location.create_location_command_handler import (
    CreateLocationCommand,
)
from app.modules.location.application.queries.get_location_by_id.get_location_by_id_handler import (
    GetLocationByIdQuery,
    GetLocationByIdResponse,
)
from app.modules.location.application.queries.get_locations.get_locations_handler import (
    FindAllLocationQuery,
    FindAllLocationQueryResponse,
)
from app.modules.share.aplication.view_models.paginated_items_view_model import (
    PaginatedItemsViewModel,
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
                                    "location_review": {
                                        "type": "string",
                                        "example": "Reseñas de la ubicacion",
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

        self.router.get(
            "/locations",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.get_locations)

        self.router.get(
            "/location/{id_location}",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.get_location_info_id)

    async def create_location(
        self,
        name_location: Annotated[str, Form()],
        phone: Annotated[str, Form()],
        address: Annotated[str, Form()],
        img_file: UploadFile,
        schedule: Annotated[str, Form()],
        location_review: Annotated[Optional[str], Form()] = None,
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
            location_review=location_review,
        )

        result: int = await self.mediator.send_async(command)
        return result

    async def get_locations(
        self, query_params: Annotated[FindAllLocationQuery, Query()]
    ) -> PaginatedItemsViewModel[FindAllLocationQueryResponse]:

        result: PaginatedItemsViewModel[FindAllLocationQueryResponse] = (
            await self.mediator.send_async(query_params)
        )
        return result

    async def get_location_info_id(
        self, query_param: Annotated[GetLocationByIdQuery, Path()]
    ) -> GetLocationByIdResponse:
        result: GetLocationByIdResponse = await self.mediator.send_async(query_param)
        return result
