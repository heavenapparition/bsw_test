from pydantic import BaseModel
from pydantic import Optional, List, PositiveFloat
import decimal
import enum


class EventState(enum.Enum):
    NEW = 'NEW'
    FINISHED_WIN = 'FINISHED_WIN'
    FINISHED_LOSE = 'FINISHED_LOSE'


class Event(BaseModel):
    event_id: int
    coefficient: Optional[PositiveFloat] = None
    deadline: Optional[int] = None
    state: Optional[EventState] = None
