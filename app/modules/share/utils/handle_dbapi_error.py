from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import DBAPIError


def handle_error(e: DBAPIError) -> None:
    cause: Optional[BaseException] = getattr(e.orig, "__cause__", None)
    if cause is not None:
        error_message = str(cause)
        raise HTTPException(status_code=400, detail=error_message)
    else:
        raise HTTPException(status_code=500, detail="Error sin causa específica")
