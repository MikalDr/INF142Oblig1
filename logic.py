from __future__ import annotations
from enum import Enum
import socket

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
    def __init__(self, id: int, advisee: User, message: Message):
        self.id = id
        self.advisee = advisee
        self.message = message
        self.advisors: list[User] = []
        self.is_answered: bool = False
        self.answers: list[Message] = []
        
    def __str__(self):
        return f"{self.id} -> {self.message.content}"
        
    def assign_advisor(self, advisor: User):
        self.advisors.append(advisor)
        
    def answer(self, message: Message):
        pass
