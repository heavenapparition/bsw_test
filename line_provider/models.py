import enum
from typing import Optional

from pydantic import BaseModel, PositiveFloat


class EventState(enum.Enum):
    NEW = "NEW"
    FINISHED_WIN = "FINISHED_WIN"
    FINISHED_LOSE = "FINISHED_LOSE"


class EventCreate(BaseModel):
    coefficient: Optional[PositiveFloat] = None
    deadline: Optional[int] = None
    state: Optional[EventState] = None


class Event(EventCreate):
    event_id: int
