import enum
from typing import Optional

from pydantic import BaseModel, PositiveFloat


class EventState(enum.Enum):
    NEW = "NEW"
    FINISHED_WIN = "FINISHED_WIN"
    FINISHED_LOSE = "FINISHED_LOSE"


class EventCreate(BaseModel):
    event_id: int
    coefficient: Optional[PositiveFloat] = None
    deadline: Optional[int] = None
    state: EventState = EventState.NEW


class Event(EventCreate):
    pass
