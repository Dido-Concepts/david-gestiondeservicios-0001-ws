from dataclasses import dataclass
from typing import Generic, List, TypeVar

T = TypeVar("T")


@dataclass
class ResponseList(Generic[T]):
    data: List[T]
    total_pages: int
    total_items: int
