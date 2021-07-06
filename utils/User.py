from uuid import uuid1
from random import randint


class User:
    __slots__ = ("username", "avatar", "color", "uuid", "group_id", "websocket")

    def __init__(self, username, avatar, color, group_id=None):
        self.username = username + f"#{randint(1000, 9999)}"
        self.avatar = avatar
        self.color = color
        self.uuid = str(uuid1())
        self.group_id = group_id

        self.websocket = None

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __eq__(self, other) -> bool:
        return self.uuid == other.uuid

    def __str__(self) -> str:
        return self.username

    def set_websocket(self, websocket):
        self.websocket = websocket

    def set_group_id(self, group_id: str):
        self.group_id = group_id
