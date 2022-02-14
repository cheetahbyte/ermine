from . import Pluggable
import typing


class Routable(Pluggable):
    def __init__(self) -> None:
        self.routes: list = []

    def get(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self.routes.append((path, handler, "get", dependencies))
            return handler

        return wrapper

    def post(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self.routes.append((path, handler, "post", dependencies))
            return handler

        return wrapper

    def put(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self.routes.append((path, handler, "put", dependencies))
            return handler

        return wrapper

    def delete(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self.routes.append((path, handler, "delete", dependencies))
            return handler

        return wrapper

    def mount(self, plug: Pluggable, prefix: str = None) -> bool:
        # if isinstance(plug, StaticFiles):
        #     self.routes.append((prefix + "/*filename", plug, "get"))
        #     return True
        if isinstance(plug, type(self)):
            for route in plug.routes:
                self.routes.append((prefix + route[0], route[1], route[2], route[3]))
            return True
