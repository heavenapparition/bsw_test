from fastapi import FastAPI, Path, HTTPException, status
from .models import Event, EventState
from .events_mocker import events_base

app = FastAPI()


@app.put('/event', status_code=status.HTTP_201_CREATED)
async def create_event(event: Event):
    if event.event_id not in events_base:
        events_base[event.event_id] = event
        return {}

    for p_name, p_value in event.dict(exclude_unset=True).items():
        setattr(events_base[event.event_id], p_name, p_value)

    return {}


@app.get('/event/{event_id}', status_code=status.HTTP_200_OK)
async def get_event(event_id: str = Path(default=None)):
    if event_id in events_base:
        return events_base[event_id]

    raise HTTPException(status_code=404, detail="Event not found")


@app.get('/events', status_code=status.HTTP_200_OK)
async def get_events():
    return list(e for e in events_base.values() if events_base.time() < e.deadline)
