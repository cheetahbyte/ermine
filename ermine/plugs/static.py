from mimetypes import MimeTypes
from . import Pluggable
from ermine.response import Response

class Static(Pluggable):
    def __init__(self, path):
        self.path: str = path

    async def __call__(self, filepath: str) -> Response:
        mime = MimeTypes()
        file_type = mime.guess_type(self.path + filepath)
        file: str = self.path + ("/" + filepath) if not self.path.endswith("/") else self.path + filepath
        with open(file, "rb") as f:
            content = f.read()
        response = Response(content, headers={"content-type": file_type[0]}, media_type=file_type[0])
        return response