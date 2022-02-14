from http.cookies import SimpleCookie
import json
from urllib.parse import parse_qsl
from multidict import CIMultiDict
from typing import Optional
from ermine.enum import ConnectionType


class Request:
    """class representing a request"""

    def __init__(self, scope: dict, receive, send) -> None:
        self._receive = receive
        self._send = send
        self._scope = scope
        self._req_headers: Optional[CIMultiDict] = None
        self._req_cookies: Optional[SimpleCookie] = None
        self.http_body: bytes = b""
        self.__http_has_more_body: bool = True
        self.__http_received_body_length: int = 0

    @property
    def path(self) -> str:
        """return the path of the request"""
        return self._scope['path']

    @property
    def method(self) -> str:
        """return the method of the request"""
        return self._scope['method'].lower()

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
    def query(self) -> dict:
        """return the query of the request"""
        return CIMultiDict(parse_qsl(self.scope.get("query_string", b"").decode("utf-8")))

    @property
    def type(self) -> str:
        """return the type of the request"""
        return ConnectionType.ws if self.scope.get("type") == "websocket" else ConnectionType.http

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