from ermine.app import Ermine
from dataclasses import dataclass
from ermine.templating import FoxTemplates
from ermine.request import Request
from ermine.static import StaticFiles
app = Ermine(title="ermine", description="")
static = StaticFiles("s")
@dataclass
class Item:
    name: str
    price: int

@app.route("/", methods=("get", "post"))
async def index(req: Request) -> str:
    if req.method == "post":
        return "Post to /"
    return templates.render("index.html", test="lol")

app.mount(static, prefix="/static")