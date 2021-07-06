import re, random
from typing import Optional
import ast
from fastapi import (
    FastAPI,
    Request,
    Response,
    Cookie,
    WebSocket,
    Form,
    WebSocketDisconnect,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from utils.ConnectionManager import ConnectionManager
from utils.Message import Message
from utils.Ratelimits import RatelimitManager

VALIDURL = re.compile(r"^([a-z\-_0-9\/\:\.]*\.(jpg|jpeg|png|gif|webp))", re.IGNORECASE)
DEFAULT_PFP = "https://cdn.discordapp.com/attachments/792686378366009354/862029567026659328/how-to-remove-profile-picture-on-zoom-12.png"
COLORS = ("purple", "pink", "red", "yellow", "green", "blue", "indigo")
SLOWDOWN = "Slow Down! 5s (Only you can see this message)"
ignore = []

app = FastAPI()
app.mount("/src/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

manager = ConnectionManager()

chatlimiter = RatelimitManager(rate=5, per=5.0)
ratelimiter = RatelimitManager(rate=1, per=5.0)


def get_response(
    template: str,
    request: Request,
    response: Response,
    data: dict = {},
) -> Response:
    data["request"] = request
    res = templates.TemplateResponse(template, data)

    return res


@app.get("/")
async def read_root(
    request: Request, response: Response, group: Optional[str] = "", error: str = ""
):
    return get_response(
        "index.html", request, response, {error: "border-red-500", "group_id": group}
    )


@app.get("/newuser")
async def new_user(
    request: Request,
    response: Response,
    username: str = "",
    avatar: str = "",
    color: str = "",
    group: str = None,
):
    if ratelimiter.check_ratelimit(str(request.client.host)):
        r = f"&group={group}" if group else ""
        if (username.strip() == "") or (not username.isalnum()) or (len(username) > 24):
            return RedirectResponse(f"/?error=username{r}")
        if avatar and not VALIDURL.match(avatar):
            return RedirectResponse(f"/?error=avatar{r}")
        if color not in COLORS:
            color = random.choice(COLORS)

        if group and not manager.group_exists(group):
            return RedirectResponse(f"/?error=group")
        client_uuid, group_id = manager.wait_user(
            username=username,
            avatar=avatar or DEFAULT_PFP,
            color=color,
            group_id=group,
        )

        return RedirectResponse(f"/chat?user={client_uuid}&group={group_id}")
    else:
        return RedirectResponse("/?error=limited")


@app.get("/chat")
async def chat(request: Request, response: Response, user: str = ""):
    if not manager.is_waiting(user):
        return RedirectResponse("/?error=failed")

    user = manager.waiting_users.get(user)
    return get_response(
        "chat.html",
        request,
        response,
        {
            "username": user.username,
            "avatar": user.avatar,
            "color": user.color,
            "default_avatar": DEFAULT_PFP,
        },
    )


@app.websocket("/ws/{group_id}/{client_uuid}")
async def websocket_endpoint(websocket: WebSocket, group_id: str, client_uuid: str):
    if (not manager.group_exists(group_id)) or (not manager.is_waiting(client_uuid)):
        return

    await manager.connect(client_uuid, websocket)
    try:
        await manager.broadcast(
            client_uuid, group_id, f"just joined the chat!", Message.EVENT
        )
        while True:
            data = await websocket.receive_text()
            if data.strip() != "":
                if chatlimiter.check_ratelimit(client_uuid):
                    await manager.broadcast(
                        client_uuid, group_id, data, Message.MESSAGE
                    )
                    if client_uuid in ignore:
                        ignore.remove(client_uuid)
                else:
                    if client_uuid not in ignore:
                        ignore.append(client_uuid)
                        await manager.send_ephemeral_event(client_uuid, SLOWDOWN)

    except WebSocketDisconnect:
        user = await manager.disconnect(client_uuid, group_id, websocket)
        if manager.group_exists(group_id):
            await manager.broadcast(
                "_", group_id, f"{user.username} has left the chat", Message.EVENT
            )
