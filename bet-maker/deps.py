from typing import Annotated
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session

from core.engine import async_session


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_pagination(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100)
) -> tuple[int, int]:
    return offset, limit


SessionDep = Annotated[AsyncSession, Depends(get_session)]
PaginationDep = Annotated[tuple[int, int], Depends(get_pagination)]
