from typing import Callable, Any
from ermine.request import Request, WebSocket
from ermine.plugs.event import EventListener
from roe_teer import Roeteer
from ermine.plugs.responder import Responder
import traceback
import typing


class Ermine:
    def __init__(
            self,
            title: str = "ermine",
            description: str = "",
            redirect_slashes: bool = True,
    ) -> None:
        self.title: str = title
        self.description: str = description
        #
        self._router = Roeteer()
        self._router._add_radix("ws")
        self.__responder = Responder()
        self.__event_listener = EventListener()

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
                handler, params = self._router.resolve(req.method, req.path)[0]
                resp = await self.__responder(req, handler, params)
                await resp(scope, receive, send)

            elif scope["type"] == "websocket":
                req = WebSocket(scope, receive, send)
                handler, params = self._router.resolve(req.method, req.path)[0]
                resp = await self.__responder(req, handler, params, ws=True)
                await resp(scope, receive, send)

        except Exception:
            traceback.print_exc()
            await send({"type": "http.response.start", "status": 500})
            await send({"type": "http.response.body", "body": b"Internal Server Error"})

    def __event_listener(self, event: str) -> None:
        # print(f"Event: {event}")
        pass

    def get(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self._router.get(path, handler)
            return handler

        return wrapper

    def post(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self._router.post(path, handler)
            return handler

        return wrapper

    def put(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self._router.put(path, handler)
            return handler

        return wrapper

    def delete(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self._router.delete(path, handler)
            return handler

        return wrapper

    def connect(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self._router.connect(path, handler)
            return handler

        return wrapper

    def patch(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self._router.patch(path, handler)
            return handler

        return wrapper

    def head(self, path: str, dependencies: list = []):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self._router.head(path, handler)
            return handler

        return wrapper

    def route(self, path: str, dependencies: list = [], methods: list | tuple = ("get",)):
        def wrapper(handler: typing.Callable) -> typing.Callable:
            for method in methods:
                self._router._get_radix(method).insert(path, handler)
            return handler

        return wrapper

    def websocket(self, path: str) -> None:
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self._router._get_radix("ws").insert(path, handler)

        return wrapper

    # def route(
    #     self, path: str, dependencies: list = [], methods: list | tuple = ("get",)
    # ):
    #     def wrapper(handler: typing.Callable) -> typing.Callable:
    #         for method in methods:
    #             self.__router.insert(method, path, handler)
    #         return handler
    #     return wrapper

    # def mount(self, plugin: Pluggable, prefix: str = None) -> None:
    #     if prefix and not prefix.startswith("/"):
    #         raise Exception("Prefix must start with '/'")

    #     if isinstance(plugin, Group):
    #         prefix = plugin.prefix or prefix
    #         if not prefix:
    #             raise Exception("Prefix cannot be empty")
    #         for path, func, method, deps in plugin.routes:
    #             if not self.__router.strict_mode and path.endswith("/"):
    #                 path = path[:-1]
    #             self.__router.add(f"{prefix}{path}", func, method, deps)
    #     if isinstance(plugin, StaticFiles):
    #         if not prefix:
    #             raise Exception("Prefix cannot be empty")
    #         self.__router.add(f"{prefix}/*filename", plugin, "get", [])

    #     return True

    def on(self, event: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def wrapper(handler: typing.Callable) -> typing.Callable:
            self.__event_listener.add(event, handler)
            return handler

        return wrapper
