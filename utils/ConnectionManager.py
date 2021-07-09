from fastapi import FastAPI, WebSocket
from typing import List, Union
from html.parser import HTMLParser
import re

from utils.User import User
from utils.Group import Group
from utils.Message import Message
from utils.ahttp import HTTP

VALIDURL = re.compile(r"([a-z\-_0-9\/\:\.]*\.(?:jpg|jpeg|png|gif|webp))", re.IGNORECASE)
URL = re.compile(
    "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})",
    re.IGNORECASE,
)
EMBEDGUTS = ("title", "image", "description")


from pprint import pprint


class MetaGrabber(HTMLParser):
    def __init__(self):
        self.metadata = {}
        super().__init__()

    def handle_starttag(self, tag, attrs):
        try:
            if tag == "meta" and len(attrs) > 1 and (attrs[0][1].startswith("og:")):
                self.metadata[attrs[0][1].strip("og:")] = attrs[1][1]
        except:
            pass

    def feed(self, html: str) -> dict:
        super().feed(html)
        data = self.metadata.copy()
        self.metadata = {}
        return data


class ConnectionManager:
    def __init__(self):
        self.waiting_users = {}
        self.active_connections = {}
        self.active_groups = {}
        self.ahttp = HTTP()
        self.grabber = MetaGrabber()
        self.cached = {}

    def wait_user(
        self, username: str, avatar: str, color: str, group_id: str = None
    ) -> [str, str]:
        user = User(username, avatar, color)
        if not group_id:
            newGroup = Group(user)
            group_id = newGroup._id
            self.active_groups[group_id] = newGroup
        else:
            self.active_groups[group_id].connect(user)

        self.waiting_users[user.uuid] = user

        return user.uuid, group_id

    def group_exists(self, group_id: str) -> bool:
        return group_id in self.active_groups

    def is_waiting(self, client_uuid: str) -> bool:
        return (client_uuid in self.waiting_users) and (
            client_uuid not in self.active_connections
        )

    async def format_message(
        self,
        client_uuid: str,
        message: str,
        _type: Union[Message.EVENT, Message.MESSAGE, Message.EPHEMERAL],
    ):
        data = {"type": _type, "message": message[:2000]}

        if _type == Message.MESSAGE:
            user = self.active_connections[client_uuid]
            data["username"] = user.username
            data["avatar"] = user.avatar
            data["color"] = user.color
            data["uuid"] = user.uuid

            embeds = []
            images = VALIDURL.findall(message)
            links = URL.findall(message)
            repeated = []
            for link in links:
                if link not in images and link not in repeated:
                    if link not in self.cached:
                        text = await self.ahttp.get_text(url=link)
                        if text:
                            metadata = self.grabber.feed(text)
                            metadata = {
                                k: v for k, v in metadata.items() if k in EMBEDGUTS
                            }
                            metadata["url"] = link
                            if "description" not in metadata:
                                metadata["description"] = ""

                            if "title" in metadata:
                                embeds.append(metadata)

                            self.cached[link] = metadata
                    else:
                        if "title" in self.cached[link]:
                            embeds.append(self.cached[link])

                repeated.append(link)
            data["embeds"] = embeds
            data["images"] = list(dict.fromkeys(images))

            return data
        elif _type == Message.EVENT:
            if client_uuid == "_":
                data["username"] = ""
            else:
                user = self.active_connections[client_uuid]
                data["username"] = user.username
            return data

        elif _type == Message.EPHEMERAL:
            return data

    async def connect(self, client_uuid: str, websocket: WebSocket):
        await websocket.accept()
        self.waiting_users[client_uuid].set_websocket(websocket)
        self.active_connections[client_uuid] = self.waiting_users.pop(client_uuid)

    async def disconnect(self, client_uuid: str, group_id: str, websocket: WebSocket):
        delete, newAuthor = self.active_groups[group_id].disconnect(client_uuid)
        if delete:
            del self.active_groups[group_id]

        if newAuthor:
            await self.send_ephemeral_event(
                newAuthor, "You have been promoted to the chat leader."
            )

        return self.active_connections.pop(client_uuid)

    async def broadcast(
        self,
        client_uuid: str,
        group_id: str,
        message: str,
        _type: Union[Message.EVENT, Message.MESSAGE, Message.EPHEMERAL],
    ):
        json_data = await self.format_message(client_uuid, message, _type)

        json_data["online"] = self.active_groups[group_id].online()

        await self.active_groups[group_id].broadcast(json_data)

    async def send_ephemeral_event(self, client_uuid: str, message: str):
        json_data = await self.format_message(client_uuid, message, Message.EPHEMERAL)
        await self.active_connections[client_uuid].websocket.send_json(json_data)
