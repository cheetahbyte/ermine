import inspect
import typing

from ermine.plugs import Pluggable
from ermine.request import BaseRequest
from ermine.response import Response, TextResponse, JsonResponse


class Responder(Pluggable):

    async def __call__(self, req: BaseRequest, handler: typing.Callable, params: dict, ws: bool = False) -> Response:
        if not handler:
            return TextResponse("Not found", 404)

        for k, v in params.items():
            params[k] = v.value

        arguments: dict = Responder._parse_arguments(req, Responder._get_handler_arguments(handler))
        # populate arguments for functions with existing params
        arguments.update(params)
        # executing the function and passing the arguments
        if inspect.iscoroutinefunction(handler):
            response: Response | typing.Any = await handler(**arguments)
            if not isinstance(response, Response):
                if type(response) == dict:
                    response = JsonResponse(response, 200)
                else:
                    if not response and ws:
                        pass
                    response = TextResponse(response, 200)
            # implement handling for other response types (pydantic & dataclass)
        else:
            response: Response | typing.Any = handler(**arguments)
            if not isinstance(response, Response):
                if type(response) == dict:
                    response = JsonResponse(response, 200)
                else:
                    if not response and ws:
                        pass
                    response = TextResponse(response, 200)
            # implement handling for other response types (pydantic & dataclass)

        if not response and not ws:
            raise Exception("no response could be generated")

        return response

    @staticmethod
    def _get_handler_arguments(handler: typing.Callable) -> list[tuple[str, inspect.Parameter]]:
        return [(name, typ) for name, typ in list(inspect.signature(handler).parameters.items())]

    @staticmethod
    def _parse_arguments(req: BaseRequest, args: list[tuple[str, inspect.Parameter]]) -> dict:
        temp: dict = dict()
        for arg in args:
            if issubclass(arg[1].annotation, BaseRequest):
                temp[arg[0]] = req
            # TODO add parsing for dataclasses and pydantic models
            else:
                if arg[0] in req.query.keys():
                    temp[arg[0]] = req.query[arg[0]]
            value = temp.get(arg[0])
            if not value:
                value = arg[1].default
        return temp
