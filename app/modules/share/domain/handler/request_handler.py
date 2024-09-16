from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TCommand = TypeVar("TCommand")
TResult = TypeVar("TResult")


class IRequestHandler(Generic[TCommand, TResult], ABC):
    @abstractmethod
    async def handle(self, command: TCommand) -> TResult:
        pass
