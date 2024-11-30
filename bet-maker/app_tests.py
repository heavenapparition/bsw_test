import pytest
from httpx import AsyncClient
from app import app
from models import EventState
import time
from sqlmodel import SQLModel
from core.engine import engine
from core.event_polling import event_polling_manager


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


@pytest.fixture
async def test_event():
    return {
        "event_id": 1,
        "coefficient": 1.5,
        "deadline": int(time.time()) + 3600,
        "state": EventState.NEW
    }


@pytest.mark.asyncio
async def test_get_events_empty():
    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        response = await ac.get("/events/")
    
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_bet_event_not_found():
    bet_data = {
        "event_id": 999,
        "amount": 100.0
    }
    
    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        response = await ac.post("/bet/", json=bet_data)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Chosen event is not available"


@pytest.mark.asyncio
async def test_create_bet_success(test_event):
    event_polling_manager._cached_events = [test_event]
    
    bet_data = {
        "event_id": test_event["event_id"],
        "amount": 100.0
    }
    
    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        response = await ac.post("/bet/", json=bet_data)
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["event_id"] == test_event["event_id"]
    assert response_data["amount"] == bet_data["amount"]
    assert response_data["state"] == test_event["state"]


@pytest.mark.asyncio
async def test_get_bets_empty():
    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        response = await ac.get("/bets/")
    
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_full_workflow(test_event):
    event_polling_manager._cached_events = [test_event]
    
    bet_data = {
        "event_id": test_event["event_id"],
        "amount": 150.0
    }
    
    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        create_response = await ac.post("/bet/", json=bet_data)
    
    assert create_response.status_code == 200
    created_bet = create_response.json()
    assert created_bet["event_id"] == test_event["event_id"]
    assert created_bet["amount"] == bet_data["amount"]
    
    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        get_response = await ac.get("/bets/")
    
    assert get_response.status_code == 200
    bets = get_response.json()
    assert len(bets) == 1
    assert bets[0]["event_id"] == test_event["event_id"]
    assert bets[0]["amount"] == bet_data["amount"]
