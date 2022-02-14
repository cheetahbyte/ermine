from ermine.injections import Depends, Inject
from ermine.response import Response, JsonResponse, TextResponse
from ermine.request import Request
from ermine.static import StaticFiles
from . import Pluggable
import inspect
import typing
import pydantic
import dataclasses

class Alternator(Pluggable):
    async def __call__(
        self,
        req: Request,
        func: typing.Callable[[], typing.Any],
        params: dict,
        deps: list,
        expect_resp: bool = True
    ) -> Response:
        # if function is none, return
        if func is None:
            return TextResponse("Not Found", 404)
        

        # arguments
        arguments: dict = dict()
        # get args of function
        args = [
            (name, typ)
            for name, typ in list(inspect.signature(func).parameters.items())
        ]

        # replace arg with request object, if arg[0][1] is instance of Request
        for arg in args:
            if arg[1].annotation == Request:
                arguments[arg[0]] = req
            elif isinstance(arg[1].default, Inject):
                dependency = await self.__call__(req, arg[1].default.injection, {}, [], expect_resp=False)
                if dependency is None:
                    return TextResponse("Failed check", 500)
                arguments[arg[0]] = dependency
            elif isinstance(arg[1].annotation, pydantic.BaseModel):
                cls = arg[1]
                arguments[arg[0]] = cls(**(await req.body()))
            elif dataclasses.is_dataclass(arg[1].annotation):
                cls = arg[1].annotation
                kwargs: dict = await req.body()
                arguments[arg[0]] = cls(**kwargs)
            else:
                if arg[0] in req.query.keys():
                    arguments[arg[0]] = req.query[arg[0]]       
            val = arguments.get(arg[0])
            if not val:
                val = arg[1].default
        # update arguments with params
        arguments.update(params)

        for dependency in deps:
            assert isinstance(dependency, Depends)
            dependency: Depends = dependency
            va: bool = await self.__call__(req, dependency.dep, {}, [], expect_resp=False)
            if va:
                continue
            else:
                return TextResponse("Failed check", 500)

        if inspect.iscoroutinefunction(func):
            response: typing.Union[Response, typing.Any] = await func(**arguments)
            if not expect_resp:
                return response
            if not isinstance(response, Response):
                if type(response) == str:
                    response = TextResponse(response, 200)
                elif type(response) == dict:
                    response = JsonResponse(response, 200)
            if isinstance(response, pydantic.BaseModel):
                response = JsonResponse(response.dict())
            if dataclasses.is_dataclass(response):
                response = JsonResponse(dataclasses.asdict(response))
            return response

        # static files
        elif isinstance(func, StaticFiles):
            resp: Response = await func(arguments["filename"])
            return resp

        # sync function
        else:
            response: typing.Union[Response, typing.Any] = func(**arguments)
            if not expect_resp:
                return response
            if not isinstance(response, Response):
                if type(response) == str:
                    response = TextResponse(response, 200)
                elif type(response) == dict:
                    response = JsonResponse(response, 200)
            if isinstance(response, pydantic.BaseModel):
                response = JsonResponse(response.dict())
            if dataclasses.is_dataclass(response):
                response = JsonResponse(dataclasses.asdict(response))
            return response