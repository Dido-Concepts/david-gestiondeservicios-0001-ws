from abc import ABC, abstractmethod
from typing import Generic, TypeVar

R = TypeVar("R")
T = TypeVar("T")


class IRequestHandler(ABC, Generic[R, T]):
    @abstractmethod
    async def handle(self, request: R) -> T:
        pass
