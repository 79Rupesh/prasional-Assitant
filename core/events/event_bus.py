from typing import Callable

from core.events.event import Event


class EventBus:
    def __init__(self):
        self._listeners = {}

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._listeners:
            self._listeners[event_name] = []

        self._listeners[event_name].append(callback)

    def publish(self, event: Event):
        listeners = self._listeners.get(event.name, [])

        for callback in listeners:
            callback(event)