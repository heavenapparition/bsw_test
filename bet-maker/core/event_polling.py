import asyncio
import time
from contextlib import asynccontextmanager
from logging import getLogger
from typing import List, Optional

from core.engine import async_session
from core.line_provider_client import LineProviderClient
from fastapi import FastAPI
from models import Event
from sqlmodel import select

logger = getLogger(__name__)


class EventPollingManager:
    """
    Класс для обновления активных событий.
    """

    def __init__(self, polling_interval: int = 1):
        self._polling_interval = polling_interval
        self._cached_events: List[Event] = []
        self._polling_task: Optional[asyncio.Task] = None
        self._is_running = False

    @property
    def cached_events(self) -> List[Event]:
        return self._cached_events

    async def _update_events(self) -> None:
        async with LineProviderClient() as client:
            events = await client.get_availible_events()
        current_timestamp = int(time.time())

        async with async_session() as session:
            for event in events:
                db_event = await session.get(Event, event.event_id)

                if db_event:
                    for key, value in event.model_dump().items():
                        setattr(db_event, key, value)
                else:
                    db_event = Event.model_validate(event.model_dump())
                    session.add(db_event)

            await session.commit()

            statement = select(Event).where(Event.deadline > current_timestamp)
            result = await session.execute(statement)
            self._cached_events = result.scalars().all()

    async def _polling_loop(self) -> None:
        self._is_running = True

        while self._is_running:
            try:
                await self._update_events()
            except Exception as e:
                logger.error(f"Error in polling loop: {str(e)}", exc_info=True)
            finally:
                await asyncio.sleep(self._polling_interval)

    def start(self) -> None:
        if not self._polling_task:
            self._polling_task = asyncio.create_task(self._polling_loop())

    async def stop(self) -> None:
        if self._polling_task:
            self._is_running = False
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
            self._polling_task = None


event_polling_manager = EventPollingManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    event_polling_manager.start()
    logger.info("Init polling")

    yield

    await event_polling_manager.stop()
    logger.info("Stopped polling")
