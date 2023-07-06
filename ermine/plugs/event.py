from . import Pluggable
import typing
import inspect
import enum


class Events(enum.IntEnum):
    STARTUP = 0
    SHUTDOWN = 1
    ON_REQUEST = 2
    ON_RESPONSE = 3


class Event(typing.NamedTuple):
    event: str
    handler: typing.Callable


class EventListener(Pluggable):

    def __init__(self) -> None:
        super().__init__()
        self.events: typing.List[Event] = []

    async def __call__(self, event: str, *args, **kwargs) -> None:
        for ev in self.events:
            if ev.event == event:
                if inspect.iscoroutinefunction(ev.handler):
                    await ev.handler(*args, **kwargs)
                else:
                    ev.handler(*args, **kwargs)

    def add(self, event: str, handler: typing.Callable):
        self.events.append(Event(event, handler))
