from fastapi import FastAPI, WebSocket
from typing import List, Union

from utils.User import User
from utils.Group import Group
from utils.Message import Message


class ConnectionManager:
    def __init__(self):
        self.waiting_users = {}
        self.active_connections = {}
        self.active_groups = {}

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

    def format_message(
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
        json_data = self.format_message(client_uuid, message, _type)
        json_data["online"] = self.active_groups[group_id].online()

        await self.active_groups[group_id].broadcast(json_data)

    async def send_ephemeral_event(self, client_uuid: str, message: str):
        json_data = self.format_message(client_uuid, message, Message.EPHEMERAL)
        await self.active_connections[client_uuid].websocket.send_json(json_data)
