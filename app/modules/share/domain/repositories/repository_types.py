from typing import List, TypeVar, Generic
from dataclasses import dataclass


T = TypeVar("T")


@dataclass
class ResponseList(Generic[T]):
    data: List[T]
    total_pages: int
    total_items: int
