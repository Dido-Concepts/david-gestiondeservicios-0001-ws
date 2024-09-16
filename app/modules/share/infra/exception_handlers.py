from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Union


async def value_error_handler(request: Request, exc: Exception) -> Union[JSONResponse]:
    if isinstance(exc, ValueError):
        return JSONResponse(status_code=400, content={"message": str(exc)})
    raise exc


async def runtime_error_handler(
    request: Request, exc: Exception
) -> Union[JSONResponse]:
    if isinstance(exc, RuntimeError):
        return JSONResponse(
            status_code=500, content={"message": "Internal server error"}
        )
    raise exc


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500, content={"message": "An unexpected error occurred"}
    )
