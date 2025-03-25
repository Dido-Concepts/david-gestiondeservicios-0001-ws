from dataclasses import dataclass
from os import getenv

import cloudinary
from cloudinary.uploader import upload
from fastapi import HTTPException, UploadFile

CLOUDINARY_CLOUD_NAME = getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = getenv("CLOUDINARY_API_SECRET", "")

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)


@dataclass
class FileUploadResponse:
    url: str
    filename: str
    content_type: str
    size: int


def is_mime_type_allowed(content_type: str, allowed_mime_types: list[str]) -> bool:
    if "*" in allowed_mime_types:
        return True
    for allowed_type in allowed_mime_types:
        if allowed_type.endswith("*"):
            prefix = allowed_type.split("*")[0]
            if content_type.startswith(prefix):
                return True
        elif content_type == allowed_type:
            return True
    return False


def upload_file(
    file: UploadFile, allowed_mime_types: list[str], max_file_size: int
) -> FileUploadResponse:
    try:

        if file.filename is None:
            raise HTTPException(
                status_code=400, detail="El archivo debe tener un nombre"
            )

        if file.content_type is None:
            raise HTTPException(
                status_code=400, detail="El archivo debe tener un tipo de contenido"
            )

        if not is_mime_type_allowed(file.content_type, allowed_mime_types):
            raise HTTPException(
                status_code=415,
                detail=f"Tipo de archivo no permitido '{file.content_type}' solo se permiten {allowed_mime_types}",
            )

        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)

        if size > max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"El archivo excede el tamaño máximo permitido {max_file_size} bytes",
            )

        result = upload(file.file)

        return FileUploadResponse(
            url=result["secure_url"],
            filename=file.filename,
            content_type=file.content_type,
            size=size,
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al subir el archivo: {str(e)}"
        )
