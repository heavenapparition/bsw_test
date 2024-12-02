import logging
import time

from core.event_polling import event_polling_manager, lifespan
from cruds import bet_crud, event_crud
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
    events = event_polling_manager.cached_events_paginated(offset, limit)
    total = event_polling_manager.cached_events_count
    return {"events": events, "total": total}


@app.post("/bet/", status_code=status.HTTP_200_OK, response_model=BetOut)
async def create_bet(bet: BetCreate, session: SessionDep):
    chosen_event = await event_crud.get(session, bet.event_id)
    if not chosen_event or chosen_event.deadline < int(time.time()):
        raise ApplicationException(
            type_=ErrorType.NOT_FOUND,
            message="Event not found",
            details={"event_id": bet.event_id},
        )
    db_bet = await bet_crud.create(session, bet.dict())
    return BetOut(
        **db_bet.model_dump(),
        state=chosen_event.state,
        coefficient=chosen_event.coefficient
    )


@app.get("/bets/", status_code=status.HTTP_200_OK, response_model=BetOutList)
async def get_bets(session: SessionDep, pagination: PaginationDep):
    offset, limit = pagination
    bets = await bet_crud.get_all_with_event_state(session, skip=offset, limit=limit)
    total = await bet_crud.count(session)

    return {"bets": bets, "total": total}
