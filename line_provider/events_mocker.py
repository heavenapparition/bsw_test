import random
import time

from models import Event, EventState


class EventsMocker:
    def __init__(self, initial_number_of_events: int = 10):
        self.events_counter = initial_number_of_events
        self.events = dict()
        self.updated_at = time.time()

        self.events.update(self.generate_events(1, initial_number_of_events))

    def generate_events(
        self, events_id_from: int = 1, events_id_to: int = 10
    ) -> dict[str, Event]:
        events = {}
        for i in range(events_id_from, events_id_to + 1):
            if self.events and str(i) in self.events.keys():
                continue
            events[str(i)] = self.create_random_event()
        return events

    def create_random_event(self) -> Event:
        return Event(
            event_id=random.randint(1, 100),
            coefficient=round(random.uniform(0.1, 5.0), 2),
            deadline=int(time.time() + random.randint(20, 120)),
            state=EventState.NEW,
        )

    def generate_additional_events(self) -> dict[str, Event]:
        if int(time.time()) > int(self.updated_at + 10):
            new_events_number = random.randint(1, 3)
            self.events.update(
                self.generate_events(
                    self.events_counter + 1, self.events_counter + new_events_number
                )
            )
            self.events_counter += new_events_number
            self.updated_at = time.time()

    def get_events(self) -> dict[str, Event]:
        for event in self.events.values():
            if time.time() > event.deadline:
                event.state = (
                    random.choice([EventState.FINISHED_WIN, EventState.FINISHED_LOSE])
                    if event.state == EventState.NEW
                    else event.state
                )
        self.generate_additional_events()
        return self.events

    def create_event(self, event_to_create: Event) -> Event:
        if event_to_create.event_id not in self.events:
            self.events[event_to_create.event_id] = event_to_create

        for p_name, p_value in event_to_create.dict(exclude_unset=True).items():
            setattr(self.events[event_to_create.event_id], p_name, p_value)
        return self.events[event_to_create.event_id]

    def get_event(self, event_id: int) -> Event:
        return self.events.get(str(event_id))


events_manager = EventsMocker(10)
