from typing import Any, Generic, Type, TypeVar

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

T = TypeVar("T")


class BaseCRUD(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, session: AsyncSession, obj_data: dict) -> T:
        obj = self.model(**obj_data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def count(self, session: AsyncSession) -> int:
        response = await session.execute(
            select(func.count()).select_from(select(self.model).subquery())
        )
        return response.scalar_one()

    async def get(self, session: AsyncSession, obj_id: int) -> T:
        result = await session.execute(
            select(self.model).where(
                self.model.__table__.primary_key.columns[0] == obj_id
            )
        )
        return result.scalars().first()

    async def get_many_by_ids(
        self,
        *,
        list_ids: list[int | str],
        filters: list[Any] | None = None,
        session: AsyncSession | None = None,
    ) -> list[T] | None:
        if filters:
            query = select(self.model).filter(
                self.model.__table__.primary_key.columns[0].in_(list_ids), *filters
            )
        else:
            query = select(self.model).where(
                self.model.__table__.primary_key.columns[0].in_(list_ids)
            )
        response = await session.execute(query)
        return response.scalars().all()

    async def get_all(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[T]:
        result = await session.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def update(self, session: AsyncSession, obj_id: int, update_data: dict) -> T:
        obj = await self.get(session, obj_id)
        if not obj:
            return None
        for key, value in update_data.items():
            setattr(obj, key, value)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, obj_id: int) -> None:
        obj = await self.get(session, obj_id)
        if obj:
            await session.delete(obj)
            await session.commit()
