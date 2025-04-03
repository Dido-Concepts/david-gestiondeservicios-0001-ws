import json
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, Path, Query, UploadFile
from mediatr import Mediator

from app.modules.auth.domain.models.user_auth_domain import UserAuth
from app.modules.auth.presentation.dependencies.auth_dependencies import (
    get_current_user,
    permission_required,
)
from app.modules.location.application.commands.change_status_location.change_status_location_command_handler import (
    ChangeStatusLocationCommand,
)
from app.modules.location.application.commands.create_location.create_location_command_handler import (
    CreateLocationCommand,
)
from app.modules.location.application.commands.update_location.update_location_command_handler import (
    UpdateLocationCommand,
)
from app.modules.location.application.commands.update_schedule_location.update_schedule_location_command_handler import (
    UpdateScheduleLocationCommand,
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

schedule_example_json = json.dumps(
    [
        {"day": "Lunes", "ranges": [{"start": "09:00", "end": "19:00"}]},
        {"day": "Martes", "ranges": []},
        {"day": "Miercoles", "ranges": []},
        {"day": "Jueves", "ranges": []},
        {"day": "Viernes", "ranges": []},
        {"day": "Sabado", "ranges": []},
        {"day": "Domingo", "ranges": []},
    ]
)

schedule_property_schema = {
    "schedule": {
        "type": "string",
        "description": "Horario semanal en formato de cadena JSON.",
        "example": schedule_example_json,
    }
}


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
                                        "example": schedule_example_json,
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

        self.router.put(
            "/location/{id_location}/status",
            dependencies=[Depends(permission_required(roles=["admin"]))],
        )(self.change_status_location)

        self.router.put(
            "/location/{id_location}/details",
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
        )(self.change_details_location)

        self.router.put(
            "/location/{id_location}/schedule",
            dependencies=[Depends(permission_required(roles=["admin"]))],
            openapi_extra={
                "requestBody": {
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": schedule_property_schema,
                                "required": ["schedule"],
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": schedule_property_schema,
                                "required": ["schedule"],
                            }
                        },
                    },
                }
            },
        )(self.change_schedule_location)

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

    async def change_status_location(
        self,
        id_location: Annotated[int, Path()],
        current_user: UserAuth = Depends(get_current_user),
    ) -> str:
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = ChangeStatusLocationCommand(
            id_location=id_location, user_updated=current_user.email
        )

        result: str = await self.mediator.send_async(command)
        return result

    async def change_details_location(
        self,
        id_location: Annotated[int, Path(ge=1, example="1")],
        name_location: Annotated[str, Form()],
        phone: Annotated[str, Form()],
        address: Annotated[str, Form()],
        location_review: Annotated[str, Form()],
        img_file: UploadFile | None = None,
        current_user: UserAuth = Depends(get_current_user),
    ) -> str:
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = UpdateLocationCommand(
            location_id=id_location,
            name=name_location,
            phone=phone,
            address=address,
            user_modify=current_user.email,
            review_location=location_review,
            img_file=img_file,
        )

        result: str = await self.mediator.send_async(command)
        return result

    async def change_schedule_location(
        self,
        id_location: Annotated[int, Path(ge=1, example="1")],
        schedule: Annotated[str, Form()],
        current_user: UserAuth = Depends(get_current_user),
    ) -> str:
        if not current_user.email:
            raise ValueError("User email not found in token")

        command = UpdateScheduleLocationCommand(
            location_id=id_location,
            schedule=schedule,
            user_modify=current_user.email,
        )

        result: str = await self.mediator.send_async(command)
        return result
