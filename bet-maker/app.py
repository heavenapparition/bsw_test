import logging

from core.event_polling import event_polling_manager, lifespan
from deps import PaginationDep, SessionDep
from exceptions.app_exception import ApplicationException, ErrorType
from exceptions.middleware import ErrorHandlingMiddleware
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from models import Bet, BetCreate, BetOut, BetOutList, EventOut, EventOutList
from sqlalchemy import func
from sqlmodel import select

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ErrorHandlingMiddleware)


@app.get("/events/", status_code=status.HTTP_200_OK, response_model=EventOutList)
async def get_events(session: SessionDep, pagination: PaginationDep):
    offset, limit = pagination
    events = event_polling_manager.cached_events
    total = len(events)
    paginated_events = [event.model_dump() for event in events[offset : offset + limit]]

    return {"events": paginated_events, "total": total}


@app.post("/bet/", status_code=status.HTTP_200_OK, response_model=BetOut)
async def create_bet(bet: BetCreate, session: SessionDep):
    chosen_event_available = any(
        event.event_id == bet.event_id for event in event_polling_manager.cached_events
    )
    if not chosen_event_available:
        raise ApplicationException(
            type_=ErrorType.NOT_FOUND,
            message="Event not found",
            details={"event_id": bet.event_id},
        )
    db_bet = Bet(**bet.dict())
    session.add(db_bet)
    await session.commit()
    await session.refresh(db_bet)
    bet_out = db_bet.model_dump() | db_bet.event.model_dump()
    return bet_out


@app.get("/bets/", status_code=status.HTTP_200_OK, response_model=BetOutList)
async def get_bets(session: SessionDep, pagination: PaginationDep):
    offset, limit = pagination
    statement = select(Bet).offset(offset).limit(limit)
    result = await session.execute(statement)
    bets = result.scalars().all()

    bets_on_return = [bet.model_dump() | bet.event.model_dump() for bet in bets]
    count_statement = select(func.count()).select_from(Bet)
    total = await session.scalar(count_statement)

    return {"bets": bets_on_return, "total": total}
