<h1 align="center">Ermine</h1>
<p align="center"> Easy, fast, stable </p>
<img src="https://cdn.discordapp.com/attachments/857979752991031296/942470898286485524/Logo1.svg" align="right" style="margin-top: -50px;"/>
<br>
<br>
Ermine is designed to provide the user with the greatest possible comfort when creating Rest APIs or entire websites.
Everything is simple and, above all, intuitively designed. No focus on superfluous configurations. Everything works, simply.

🔑 Key features

- intuitive, due to the clear design
- simple, due to the fast learning curve
- practical, through the great editor support
- minimalistic, no superfluous functions

#### What is Ermine and what is not


Ermine is not a HighSpeed framework. Ermine is probably not ready for production. Ermine is a spare time project of mine. Ermine is self-contained. It doesn't need anything, except for an ASGI server. So it's like Starlette.
I would appreciate if you use Ermine, try it and give me your feedback.

#### Participate in Ermine

You are welcome to collaborate on Ermine. However, you should maintain the codestyle, and also follow PEP 8 (the Python style guide).

#### Ermine disadvantages

Ermine is still deep in development, which is why some features are still missing. 

- Websockets

#### Examples

Here is the most basic example of ermine

```py
from ermine import Ermine, Request

app = Ermine()

@app.get("/home")
async def home():
	return "Welcome home"
```

You want to build a RestAPI? No problem

```py
from ermine import Ermine, Request


app = Ermine()
templates = FoxTemplates("templates")

@app.get("/api")
def api():
	return {"name": "Leo", "age": 16}
```

You want to send HTML files? Ermine got your back

```py
from ermine import Ermine, Request
from ermine.responses import HTMLResponse


app = Ermine()

@app.get("/html")
async def home():
	with open("home.html", "r") as f:
		data = f.read()
	return HTMLResponse(data)
```

You want to use some templates ? You want to load templates? No problem with [Fuchs](https://github.com/cheetahbyte/fuchs)

```py
from ermine import Ermine, Request
from ermine.templating import FoxTemplates

app = Ermine()
templates = FoxTemplates("templates")

@app.get("/home")
async def home():
	return templates.render("home.html", name="Leo")
```

**Changes incoming**
<center>

Join our [discord](https://discord.gg/EtqGfBVuZS) !

<img src="https://images.unsplash.com/photo-1548714859-18c34a4c384a?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1074&q=80" alt="Ermine" style="height: 300px" /></center>
