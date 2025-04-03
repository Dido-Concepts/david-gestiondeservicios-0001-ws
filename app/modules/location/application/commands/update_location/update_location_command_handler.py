import re
from typing import Optional
from fastapi import UploadFile
from mediatr import Mediator
from pydantic import BaseModel, field_validator

from app.constants import injector_var

from app.modules.location.domain.repositories.location_repository import (
    LocationRepository,
)

from app.modules.share.domain.handler.request_handler import IRequestHandler
from app.modules.share.infra.upload_files.service_cloudinary import upload_file


class UpdateLocationCommand(BaseModel):
    location_id: int
    name: str
    phone: str
    address: str
    user_modify: str
    review_location: str
    img_file: UploadFile | None = None

    @field_validator("name")
    def validate_name_location(cls, v: str) -> str:
        if not re.match(r"^[A-ZÁÉÍÓÚÜÑáéíóúüña-z0-9 ]+$", v):
            raise ValueError("name no debe contener caracteres especiales")
        return v

    @field_validator("phone")
    def validate_phone(cls, v: str) -> str:
        if not v.isdigit() or not v.startswith("9") or len(v) != 9:
            raise ValueError(
                "phone debe ser un número de 9 dígitos que comience con '9'"
            )
        return v

    @field_validator("address")
    def validate_address(cls, v: str) -> str:
        if not re.match(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 .#]+$", v):
            raise ValueError(
                "address solo debe contener letras, números, espacios, '.', o '#'"
            )
        return v

    @field_validator("review_location")
    def validate_location_review(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 .,#]+$", v):
            raise ValueError(
                "review_location solo debe contener letras, números, espacios, ',', '#' o '.'"
            )
        return v


@Mediator.handler
class UpdateLocationCommandHandler(IRequestHandler[UpdateLocationCommand, str]):
    def __init__(self) -> None:
        injector = injector_var.get()
        self.location_repository = injector.get(LocationRepository)  # type: ignore[type-abstract]

    async def handle(self, command: UpdateLocationCommand) -> str:

        new_file_url: Optional[str] = None
        new_file_filename: Optional[str] = None
        new_file_content_type: Optional[str] = None
        new_file_size: Optional[int] = None

        if command.img_file is not None:
            img = upload_file(
                file=command.img_file,
                allowed_mime_types=["image/*"],
                max_file_size=2_000_000,
            )
            new_file_url = img.url
            new_file_filename = img.filename
            new_file_content_type = img.content_type
            new_file_size = img.size

        result = await self.location_repository.update_details_location(
            location_id=command.location_id,
            name=command.name,
            phone=command.phone,
            address=command.address,
            user_modify=command.user_modify,
            review_location=command.review_location,
            new_file_url=new_file_url,
            new_file_filename=new_file_filename,
            new_file_content_type=new_file_content_type,
            new_file_size=new_file_size,
        )

        return result
