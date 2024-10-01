from typing import AsyncIterator

from app.database import create_session
from app.modules.share.infra.persistence.unit_of_work import UnitOfWork


async def get_uow() -> AsyncIterator[UnitOfWork]:
    async with UnitOfWork(session_factory=create_session) as uow:
        yield uow
