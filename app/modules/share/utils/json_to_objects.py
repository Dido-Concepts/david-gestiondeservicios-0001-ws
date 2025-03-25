import json
from typing import Type, TypeVar

from fastapi import HTTPException

T = TypeVar("T")


def json_to_objects(json_string: str, cls: Type[T]) -> list[T]:
    try:
        data = json.loads(json_string)
        if not isinstance(data, list):
            raise ValueError("El JSON debe ser una lista de objetos")
        return [cls(**item) for item in data]
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Formato JSON inválido")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
