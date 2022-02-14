from ermine.groups import Group
from ermine.plugs import Pluggable
from ermine.request import Request
from ermine.router import BaseRouter
from ermine.plugs.alternator import Alternator
from ermine.plugs.event import Eventlistener
from ermine.static import StaticFiles
import traceback
import typing


class Ermine:
    def __init__(
        self,
        title: str = "ermine",
        description: str = "",
        strict: bool = False,
        redirect_slashes: bool = False,
    ) -> None:
        self.title: str = title
        self.description: str = description
        #
        self.__router = BaseRouter(redirect_slashes, strict)
        self.__alternator = Alternator()
        self.__event_listener = Eventlistener()

    async def __call__(self, scope: dict, receive, send) -> None:
        try:
            if scope["type"] == "lifespan":
                message = await receive()
                if message["type"] == "lifespan.startup":
                    await self.__event_listener("startup")
                    await self.__event_listener(message["type"])
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    await self.__event_listener("shutdown")
                    await self.__event_listener(message["type"])
                    await send({"type": "lifespan.shutdown.complete"})
                    return

            elif scope["type"] == "http":
                req = Request(scope, receive, send)
                func, params, deps = await self.__router.get(req.path, req.method)
                resp = await self.__alternator(req, func, params, deps)
                await resp(scope, receive, send)

        except:
            traceback.print_exc()
            await send({"type": "http.response.start", "status": 500})
            await send({"type": "http.response.body", "body": b"Internal Server Error"})

    def __event_listener(self, event: str) -> None:
        # print(f"Event: {event}")
        pass

    def get(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self.__router.add(path, handler, "get", dependencies)
            return handler

        return wrapper

    def post(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self.__router.add(path, handler, "post", dependencies)
            return handler

        return wrapper

    def put(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self.__router.add(path, handler, "put", dependencies)
            return handler

        return wrapper

    def delete(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self.__router.add_route(path, handler, "delete", dependencies)
            return handler

        return wrapper

    def route(
        self, path: str, dependencies: list = [], methods: list | tuple = ("get",)
    ):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self.__router.add(path, handler, methods, dependencies)
            return handler

        return wrapper

    def mount(self, plugin: Pluggable, prefix: str = None) -> None:
        if prefix and not prefix.startswith("/"):
            raise Exception("Prefix must start with '/'")

        if isinstance(plugin, Group):
            prefix = plugin.prefix or prefix
            if not prefix:
                raise Exception("Prefix cannot be empty")
            for path, func, method, deps in plugin.routes:
                if not self.__router.strict_mode and path.endswith("/"):
                    path = path[:-1]
                self.__router.add(f"{prefix}{path}", func, method, deps)
        if isinstance(plugin, StaticFiles):
            if not prefix:
                raise Exception("Prefix cannot be empty")
            self.__router.add(f"{prefix}/*filename", plugin, "get", [])

        return True

    def on(self, event: str) -> None:
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self.__event_listener.add(event, handler)
            return handler

        return wrapper