from http.cookies import BaseCookie, SimpleCookie
import json
import typing


class Response:
    """
    The Response class is used to return data from a request.
    """

    media_type: str | None = None
    charset: str = "utf-8"

    def __init__(
        self,
        content: typing.Any,
        status: int = 200,
        headers: dict | None = None,
        media_type: str | None = None,
    ) -> None:
        self.status: int = status
        self.content: typing.Any = content
        if media_type:
            self.media_type = media_type
        self.body = self.render(content)
        self.set_headers(headers)

    def render(self, content: typing.Any) -> bytes:
        if content is None:
            return b""

        if isinstance(content, bytes):
            return content

        return content.encode(self.charset)

    def set_headers(self, headers: None | typing.Mapping[str, str] = None) -> None:
        if headers is None:
            raw_headers: typing.List[typing.Tuple[bytes, bytes]] = []
        else:
            raw_headers = [
                (k.encode(self.charset), v.encode(self.charset))
                for k, v in headers.items()
            ]

        body: bytes = getattr(self, "body", b"")
        if body:
            raw_headers.append(("Content-Length", str(len(body)).encode(self.charset)))
        ctype: str = self.media_type
        if ctype:
            if ctype.startswith("text/"):
                ctype += ";" + "charset=" + self.charset + ";"
            raw_headers.append((b"content-type", ctype.encode(self.charset)))
        self.headers = raw_headers

    def set_cookie(
        self,
        key: str,
        value: str = "",
        max_age: int = None,
        expires: int = None,
        path: str = "/",
        domain: str = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: str = "lax",
    ) -> None:
        """Adds a cookie to the answer"""
        cookie: BaseCookie = SimpleCookie()
        cookie[key] = value
        if max_age:
            cookie[key]["max-age"] = max_age
        if expires:
            cookie[key]["expires"] = expires
        if path:
            cookie[key]["path"] = path
        if domain:
            cookie[key]["domain"] = domain
        if secure:
            cookie[key]["secure"] = True
        if httponly:
            cookie[key]["httponly"] = True
        if samesite is not None:
            assert samesite.lower() in [
                "strict",
                "lax",
                "none",
            ], "samesite must be 'strict', 'lax' or 'none'"
            cookie[key]["samesite"] = samesite
        cookie_val = cookie.output(header="").strip()
        self.headers.append((b"set-cookie", cookie_val.encode("latin-1")))

    async def __call__(self, scope, receive, send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status,
                "headers": self.headers,
            }
        )
        await send({"type": "http.response.body", "body": self.body})


class HTMLResponse(Response):
    media_type = "text/html"

class JsonResponse(Response):
    media_type = "application/json"


    def render(self, content: dict) -> bytes:
        return json.dumps(content, indent=None).encode("utf-8")


class TextResponse(Response):
    media_type = "text/plain"

    