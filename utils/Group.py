from uuid import uuid1
from random import choice

from utils.User import User
from utils.Message import Message


class Group:
    __slots__ = ("author", "_id", "members")

    def __init__(self, author):
        self.author = author.uuid
        self._id = str(abs(hash(uuid1())))
        self.members = {author.uuid: author}

    def connect(self, user):
        self.members[user.uuid] = user

    def disconnect(self, user_uuid: str) -> bool:
        newAuthor = False
        if self.online() == 1:
            return True, newAuthor

        self.members.pop(user_uuid)

        if user_uuid == self.author:
            newAuthor = choice(list(self.members.keys()))
            self.author = newAuthor

        return False, newAuthor

    def online(self) -> int:
        return len(self.members)

    async def broadcast(
        self,
        json_data: dict,
    ):
        if json_data["type"] == Message.MESSAGE:
            json_data["author"] = self.author
        for member in self.members.values():
            if member.websocket:
                await member.websocket.send_json(json_data)
