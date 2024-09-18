from types import TracebackType
from typing import Any, Callable, Coroutine, Optional

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    def __init__(
        self, session_factory: Callable[[], Coroutine[Any, Any, AsyncSession]]
    ):
        self._session_factory: Callable[[], Coroutine[Any, Any, AsyncSession]] = (
            session_factory
        )
        self._session: Optional[AsyncSession] = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Session not initialized. Use within 'async with'.")
        return self._session

    async def __aenter__(self) -> "UnitOfWork":
        self._session = await self._session_factory()
        await self._session.begin()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if exc_value is None:
            await self.commit()
        else:
            await self.rollback()
        await self.close()

    async def commit(self) -> None:
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()

    async def close(self) -> None:
        if self._session:
            await self._session.close()
