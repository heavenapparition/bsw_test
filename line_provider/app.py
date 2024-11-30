from events_mocker import events_manager
from fastapi import FastAPI, HTTPException, status
from models import Event

app = FastAPI()


@app.put("/event/", status_code=status.HTTP_201_CREATED, response_model=Event)
async def create_event(event_to_create: Event):
    created_event = events_manager.create_event(event_to_create)
    return created_event


@app.get("/event/{event_id}/", status_code=status.HTTP_200_OK, response_model=Event)
async def get_event(event_id: str):
    event = events_manager.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.get("/events/", status_code=status.HTTP_200_OK, response_model=dict[str, Event])
async def get_events():
    events = events_manager.get_events()
    return events
