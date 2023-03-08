from __future__ import annotations
from enum import Enum
from socket import socket

MESSAGE_SIZE = 1024
"""Message size, in bytes"""

SERVER_DISCONNECT_COMMAND = "DISCONNECT_COMMAND"
"""Disconnect command"""


class User:
    def __init__(self, id: bytes, role: Role, sock: socket):
        self.id = id
        self.role = role
        self.sock = sock

    def __str__(self):
        return str(self.id.decode())


class Role(Enum):
    Advisee = 0
    Advisor = 1

    def __str__(self):
        return "Advisee" if self == Role.Advisee else "Advisor"


class Message:
    def __init__(self, sender: User, content: str):
        self.sender = sender
        self.content = content

    def __str__(self):
        return f"{self.sender} -> {self.content}"


class Situation:
    def __init__(self, advisee: User, message: Message):
        self.advisee = advisee
        self.message = message
        self.advisor: User = None
        self.answer: Message = None

    def __str__(self):
        return f"{self.id} -> {self.message.content}"
