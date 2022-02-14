from . import Pluggable
import typing
import inspect

class __Event(typing.NamedTuple):
    event: str
    handler: typing.Callable

class Eventlistener(Pluggable):

    def __init__(self) -> None:
        super().__init__()
        self.events: typing.List[__Event] = []

    async def __call__(self, event: str,*args, **kwargs) -> None:
        for event in self.events:
            if event.event == event:
                if inspect.iscoroutinefunction(event.handler):
                    await event.handler(*args, **kwargs)
                else:
                    event.handler(*args, **kwargs)


    def add(self, event: str, handler: typing.Callable):
        self.events.append(__Event(event, handler))