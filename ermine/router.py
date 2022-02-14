import typing
from wire_rxtr import RadixTree


class BaseRouter:
    """"""

    __slots__ = ("routes", "redirect_slashes", "strict_mode")

    def __init__(self, redirect_slashes: bool = False, strict_mode: bool = False) -> None:
        self.redirect_slashes: bool = redirect_slashes
        self.strict_mode: bool = strict_mode
        self.routes = RadixTree()

    def add(
        self, path: str, handler, method: str | list, dependencies: list = []
    ) -> bool | None:
        if not self.strict_mode:
            path = path[:-1] if path.endswith("/") and len(path) > 1 else path
        self.routes.insert(path, handler, method, dependencies)
        return True

    async def get(
        self, path: str, method: str
    ) -> typing.Tuple[typing.Callable, dict, list] | None:
        if not self.strict_mode:
            path = path[:-1] if path.endswith("/") and len(path) > 1 else path
        pathFound, handler, params, dependencies = self.routes.get(path, method)
        if pathFound:
            return handler, params, dependencies
        return None, None, None