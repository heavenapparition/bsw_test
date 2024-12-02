from models import Bet, Event
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_crud import BaseCRUD


class BetCRUD(BaseCRUD[Bet]):
    def __init__(self):
        super().__init__(Bet)

    async def get_all_by_event_id(
        self, session: AsyncSession, event_id: int
    ) -> list[Bet]:
        result = await session.execute(
            select(self.model).where(self.model.event_id == event_id)
        )
        return result.scalars().all()

    async def get_all_with_event_state(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[dict]:
        result = await session.execute(
            select(self.model, Event.state, Event.coefficient)
            .join(Event, self.model.event_id == Event.event_id)
            .offset(skip)
            .limit(limit)
        )
        return [
            {**bet.model_dump(), "state": state, "coefficient": coef}
            for bet, state, coef in result.all()
        ]


bet_crud = BetCRUD()
