import time

from models import Event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .base_crud import BaseCRUD


class EventCRUD(BaseCRUD[Event]):
    def __init__(self):
        super().__init__(Event)

    async def get_all_availiable(self, session: AsyncSession) -> list[Event]:
        statement = select(Event).where(Event.deadline > int(time.time()))
        result = await session.execute(statement)
        return result.scalars().all()


event_crud = EventCRUD()
