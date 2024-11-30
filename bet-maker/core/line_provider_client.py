import logging
from typing import List, Optional

import httpx
from core.config import settings
from models import Event, EventOut

logger = logging.getLogger(__name__)


class LineProviderClient:
    def __init__(self, base_url: Optional[str] = None, timeout: float = 10.0):
        self.base_url = base_url or settings.LINE_PROVIDER_BASE_URL
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    async def get_availible_events(self) -> List[EventOut]:
        response = await self._client.get("/events/")
        response.raise_for_status()

        events_data = response.json()
        events = [Event(**event) for event in events_data.values()]
        return events

    async def get_event(self, event_id: int) -> Optional[Event]:
        """Fetch specific event by ID"""
        response = await self._client.get(f"/event/{event_id}/")

        if response.status_code == 404:
            logger.warning(f"Event {event_id} not found in line provider")
            return None

        response.raise_for_status()
        event = Event(**response.json())
        logger.info(f"Successfully fetched event {event_id}")
        return event

    async def close(self):
        await self._client.aclose()
