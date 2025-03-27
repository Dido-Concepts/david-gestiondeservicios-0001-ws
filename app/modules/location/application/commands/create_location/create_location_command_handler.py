from dataclasses import dataclass
from typing import Optional

from fastapi import UploadFile
from mediatr import Mediator

from app.constants import injector_var
from app.modules.location.application.request.create_location_request import (
    CreateLocationRequest,
    ScheduleRequest,
)
from app.modules.location.domain.entities.location_domain import ScheduleRequestDomain
from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)
from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.share.infra.upload_files.service_cloudinary import upload_file
from app.modules.share.utils.json_to_objects import json_to_objects


@dataclass
class CreateLocationCommand:
    name_location: str
    phone: str
    address: str
    img_file: UploadFile
    schedule: str
    user_create: str
    location_review: Optional[str] = None


@Mediator.handler
class CreateLocationCommandHandler(IRequestHandler[CreateLocationCommand, int]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.location_repository = injector.get(LocationRepository)  # type: ignore[type-abstract]

    async def handle(self, command: CreateLocationCommand) -> int:

        schedule_list = json_to_objects(
            json_string=command.schedule, cls=ScheduleRequest
        )

        img = upload_file(
            file=command.img_file,
            allowed_mime_types=["image/*"],
            max_file_size=2_000_000,
        )

        location_request = CreateLocationRequest(
            address=command.address,
            phone=command.phone,
            name_location=command.name_location,
            schedule=schedule_list,
            location_review=command.location_review,
        )

        schedule_list_request = [
            ScheduleRequestDomain(dia=s.day, inicio=s.start_time, fin=s.end_time)
            for s in location_request.schedule
        ]

        id_location = await self.location_repository.create_Location(
            name_location=location_request.name_location,
            phone=location_request.phone,
            address=location_request.address,
            file_url=img.url,
            file_name=img.filename,
            file_content_type=img.content_type,
            file_size=img.size,
            schedule=schedule_list_request,
            user_create=command.user_create,
            location_review=location_request.location_review,
        )

        return id_location
