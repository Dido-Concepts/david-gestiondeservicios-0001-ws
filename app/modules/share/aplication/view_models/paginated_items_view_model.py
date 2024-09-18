from typing import List, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class MetaPaginatedItemsViewModel(BaseModel):
    page: int
    page_size: int
    page_count: int
    total: int


class PaginatedItemsViewModel(BaseModel, Generic[T]):
    data: List[T]
    meta: MetaPaginatedItemsViewModel
