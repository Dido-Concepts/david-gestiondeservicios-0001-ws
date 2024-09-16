from typing import Type, Dict, Any
from app.modules.share.domain.handler.request_handler import IRequestHandler


class UserMediator:
    def __init__(self) -> None:
        self._handlers: Dict[Type[Any], IRequestHandler[Any, Any]] = {}

    def register_handler(
        self, key: Type[Any], handler: IRequestHandler[Any, Any]
    ) -> None:
        """Registra un handler para un comando o consulta específico."""
        self._handlers[key] = handler

    async def send(self, request: Any) -> Any:
        """Envía un comando o consulta al handler correspondiente."""
        handler = self._handlers.get(type(request))
        if handler is None:
            raise ValueError(f"No handler found for {type(request)}")
        return await handler.handle(request)
