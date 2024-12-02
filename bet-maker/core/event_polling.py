import asyncio
import time
from contextlib import asynccontextmanager
from logging import getLogger
from typing import List, Optional

from core.engine import async_session
from core.line_provider_client import LineProviderClient
from cruds import bet_crud, event_crud
from fastapi import FastAPI
from models import Event
from sqlalchemy.ext.asyncio import AsyncSession
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

    @property
    def cached_events_count(self) -> int:
        return len(self._cached_events)

    def cached_events_paginated(self, offset: int, limit: int) -> List[Event]:
        return self._cached_events[offset : offset + limit]

    async def _get_line_provider_events(self) -> List[Event]:
        async with LineProviderClient() as client:
            return await client.get_availible_events()

    async def _upsert_events_to_db(self, fetched_events: List[Event]) -> None:
        async with async_session() as session:
            for event in fetched_events:
                db_event = await event_crud.get(session, event.event_id)
                if db_event:
                    db_event = await event_crud.update(
                        session, event.event_id, event.model_dump()
                    )
                else:
                    db_event = await event_crud.create(session, event.model_dump())
            await session.commit()
            self._cached_events = await event_crud.get_all_availiable(session)

    async def _update_events(self) -> None:
        events = await self._get_line_provider_events()
        await self._upsert_events_to_db(events)

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
