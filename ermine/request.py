import json
from http.cookies import SimpleCookie
from typing import Optional, Any
from urllib.parse import parse_qsl

from multidict import CIMultiDict

from ermine.enum import ConnectionType


class BaseRequest:
    """class representing a basic request to the server"""

    def __init__(self, scope: dict, receive, send) -> None:
        self._receive = receive
        self._send = send
        self._scope = scope
        self._req_headers: Optional[CIMultiDict] = None
        self._req_cookies: Optional[SimpleCookie] = None

    @property
    def path(self) -> str:
        return self._scope["path"]

    @property
    def headers(self) -> CIMultiDict:
        """return the headers of the request"""
        if not self._req_headers:
            self._req_headers = CIMultiDict(
                [(k.decode("ascii"), v.decode("ascii")) for (k, v) in self._scope["headers"]])
        return self._req_headers

    @property
    def client(self) -> str:
        """return the client of the request"""
        return self._scope['client']

    @property
    def cookies_raw(self) -> SimpleCookie:
        """return the raw cookies of the request"""
        if not self._req_headers:
            self._req_headers = CIMultiDict(
                [(k.decode("ascii"), v.decode("ascii")) for (k, v) in self._scope["headers"]])
            self._req_cookies.load(self._req_headers.get("cookie", {}))
        return self._req_cookies

    @property
    def cookies(self) -> dict:
        """return the cookies of the request"""
        return {key: m.value for key, m in self.cookies_raw.items()}

    @property
    def scope(self) -> dict:
        """return the scope of the request"""
        return self._scope

    @property
    def query(self) -> CIMultiDict[Any]:
        """return the query of the request"""
        return CIMultiDict(parse_qsl(self.scope.get("query_string", b"").decode("utf-8")))

    @property
    def type(self) -> ConnectionType:
        """return the type of the request"""
        return ConnectionType.ws if self.scope.get("type") == "websocket" else ConnectionType.http

    async def handle(self, message):
        return NotImplemented


class Request(BaseRequest):
    """class representing a request"""

    def __init__(self, scope: dict, receive, send) -> None:
        super().__init__(scope, receive, send)
        self.http_body: bytes = b""
        self.__http_has_more_body: bool = True
        self.__http_received_body_length: int = 0

    @property
    def method(self) -> str:
        """return the method of the request"""
        return self._scope['method'].lower()

    async def handle(self, message) -> None:
        if message.get("type") == "http.disconnect":
            raise Exception("Disconnect")

    async def __body_iter(self):
        if not self.type == ConnectionType.http:
            raise Exception("Not an HTTP connection")
        if self.__http_received_body_length > 0 and self.__http_has_more_body:
            raise Exception("body iter is already started and is not finished")
        if self.__http_received_body_length > 0 and not self.__http_has_more_body:
            yield self.http_body

        req_body_length: int | None = (int(self.headers.get("content-length", "0"))
                                       if not self.headers.get("transfer-encoding") == "chunked"
                                       else None)

        while self.__http_has_more_body:
            if req_body_length and self.__http_received_body_length > req_body_length:
                raise Exception("body length exceeded")

            message = await self._receive()
            message_type: str = message.get("type")
            await self.handle(message)
            if message_type != "http.request":
                continue
            chunk: bytes = message.get("body", b"")
            if not isinstance(chunk, bytes):
                raise RuntimeError("Chunk is not bytes")
            self.http_body += chunk
            self.__http_has_more_body = message.get("more_body", False)
            self.__http_received_body_length += len(chunk)
            yield bytes(chunk)

    async def body(self) -> bytes | dict:
        """return the body of the request"""
        data: bytes = b"".join([chunk async for chunk in self.__body_iter()])
        try:
            return json.loads(data)
        except json.decoder.JSONDecodeError:
            return data


class WebSocket(BaseRequest):

    def __init__(self, scope: dict, receive, send):
        super().__init__(scope, receive, send)
        self.method = "ws"

    async def accept(self) -> None:
        """accepts client on websocket"""
        await self._send({
            "type": "websocket.accept"
        })

    async def _receive_raw(self) -> str:
        """retrieves whatever the websocket sends in raw"""
        msg = await self._receive()
        if msg["type"] == "websocket.receive":
            return msg["text"]

    async def receive_json(self) -> dict | None:
        """parses message to json, returns none if error occurs"""
        raw = await self._receive_raw()
        if raw:
            try:
                return json.loads(raw)
            except json.decoder.JSONDecodeError:
                return None

    async def receive_text(self) -> str | None:
        """retrieves message as plain str"""
        return str(await self._receive_raw())

    async def close(self, status: int = 1000, reason: str = ""):
        """closes connection to websocket"""
        await self._send({"type": "websocket.close", "status": status, "reason": reason})
