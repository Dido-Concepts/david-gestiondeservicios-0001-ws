from typing import Union

from fastapi import Request
from fastapi.responses import JSONResponse


from app.modules.share.domain.exceptions import (
    InvalidFieldsException,
    InvalidFiltersException,
)


async def value_error_handler(request: Request, exc: Exception) -> Union[JSONResponse]:
    if isinstance(exc, ValueError):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "status": 400,
                    "name": "BadRequestError",
                    "message": str(exc),
                }
            },
        )
    raise exc


async def runtime_error_handler(
    request: Request, exc: Exception
) -> Union[JSONResponse]:
    if isinstance(exc, RuntimeError):
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "status": 500,
                    "name": "InternalServerError",
                    "message": "Internal server error",
                }
            },
        )
    raise exc


async def invalid_fields_exception_handler(
    request: Request, exc: Exception
) -> Union[JSONResponse]:
    if isinstance(exc, InvalidFieldsException):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "status": 400,
                    "name": "InvalidFieldsError",
                    "message": str(exc),
                }
            },
        )
    raise exc


async def invalid_filters_exception_handler(  # NUEVO HANDLER
    request: Request, exc: Exception
) -> Union[JSONResponse]:
    if isinstance(exc, InvalidFiltersException):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "status": 400,
                    "name": "InvalidFiltersError",
                    "message": str(exc),
                }
            },
        )
    raise exc


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "status": 500,
                "name": "InternalServerError",
                "message": "An unexpected error occurred",
            }
        },
    )
