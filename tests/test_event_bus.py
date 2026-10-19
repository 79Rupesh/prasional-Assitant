from core.events.event import Event
from core.events.event_bus import EventBus


def on_test_event(event):
    print(f"Received event: {event.name}")
    print(f"Data: {event.data}")


bus = EventBus()

bus.subscribe("test_event", on_test_event)

event = Event(
    name="test_event",
    data={"message": "Hello from Ela"}
)

bus.publish(event)