from .models import Event, EventState
import random
import time

class EventsMocker:
    @staticmethod
    def generate_events(number: int) -> dict[str, Event]:
        events = {}
        for i in range(1, number + 1):
            events[str(i)] = Event(
                event_id=i,
                coefficient=round(random.uniform(0.1, 5.0), 2),
                deadline=int(time.time()) + random.randint(60, 600),
                state=EventState.NEW
            )
        return events

events_base = EventsMocker.generate_events(10)
