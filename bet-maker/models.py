import enum
from typing import List, Optional

from pydantic import NonNegativeInt, PositiveFloat
from sqlmodel import Field, Relationship, SQLModel


class EventState(str, enum.Enum):
    NEW = "NEW"
    FINISHED_WIN = "FINISHED_WIN"
    FINISHED_LOSE = "FINISHED_LOSE"


class EventBase(SQLModel):
    coefficient: Optional[PositiveFloat] = None
    deadline: Optional[int] = None
    state: Optional[EventState] = None


class EventCreate(EventBase):
    pass


class Event(EventBase, table=True):
    __tablename__ = "event"

    event_id: Optional[int] = Field(default=None, primary_key=True)
    bets: List["Bet"] = Relationship(
        back_populates="event", sa_relationship_kwargs={"lazy": "selectin"}
    )


class EventOut(EventBase):
    event_id: int


class BetBase(SQLModel):
    event_id: int = Field(foreign_key="event.event_id")
    amount: PositiveFloat


class Bet(BetBase, table=True):
    __tablename__ = "bet"

    bet_id: Optional[int] = Field(default=None, primary_key=True)
    event: Event = Relationship(
        back_populates="bets",
        sa_relationship_kwargs={
            "lazy": "noload",
            "cascade": "all, delete-orphan",
            "single_parent": True,
        },
    )


class BetCreate(BetBase):
    pass


class BetOut(BetBase):
    bet_id: int
    state: EventState
    coefficient: PositiveFloat


class BetOutList(SQLModel):
    bets: List[BetOut]
    total: NonNegativeInt


class EventOutList(SQLModel):
    events: List[EventOut]
    total: NonNegativeInt
