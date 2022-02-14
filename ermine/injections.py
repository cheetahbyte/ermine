import inspect
import typing


class Inject:
    """
    Injectable class.
    """
    def __init__(self, injection) -> None:
        self.injection = injection


    async def __call__(self, **kwargs) -> typing.Any:
        if inspect.iscoroutinefunction(self.dep):
            return await self.dep(**kwargs)
        else:
            return self.dep(**kwargs)
class Depends:
    """
    Dependency class.
    """
    def __init__(self, dep) -> None:
        self.dep = dep


    async def __call__(self, **kwargs) -> bool:
        if inspect.iscoroutinefunction(self.dep):
            return await self.dep(**kwargs)
        else:
            return self.dep(**kwargs)
  