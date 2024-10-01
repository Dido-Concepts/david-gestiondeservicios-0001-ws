from typing import Dict, Generic, Optional, Type, TypeVar

from app.modules.share.domain.handler.request_handler import IRequestHandler

R = TypeVar("R")
T = TypeVar("T")


class Mediator(Generic[R, T]):
    def __init__(self) -> None:
        self._handlers: Dict[Type[R], IRequestHandler[R, T]] = {}

    def register_handler(self, key: Type[R], handler: IRequestHandler[R, T]) -> None:
        self._handlers[key] = handler

    async def send(self, request: R) -> T:
        handler: Optional[IRequestHandler[R, T]] = self._handlers.get(type(request))
        if handler is None:
            raise ValueError(f"No handler found for {type(request)}")
        return await handler.handle(request)
