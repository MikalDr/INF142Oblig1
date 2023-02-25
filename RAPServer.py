from __future__ import annotations
from socket import create_server
from logic import User, Role, Situation, Message
import random
import _thread

MESSAGE_SIZE = 1024
sit_count = 0
users:dict[Role: list[User]] = {Role.Advisee:[], Role.Advisor:[]}
situations:dict[int: Situation] = {}

with open("animals.txt", "r") as f:
    animals = f.read().splitlines()
    
with open("adjectives.txt", "r") as f:
    adjectives = f.read().splitlines()

def assign_name() -> str:
    return random.choice(adjectives) + "" + random.choice(animals)

def assign_role() -> Role:
    if(len(users.get(Role.Advisee)) == 0):
        return Role.Advisee
    else:
        return random.choice([Role.Advisee, Role.Advisor])

def get_situation(u = None) -> str:
    return "\n".join([str(sit) for sit in situations.values()]) if u is None else "\n".join([str(sit) for sit in situations.values() if sit.user.id == u.id])

def client(socket, u):
    global sit_count
    while True:
        request_message = conn.recv(1024)
        repl = request_message.decode().split(" ")
        if(len(repl) > 1):
            cmd, sit_id = repl
            sit_id = int(sit_id)
        else:
            cmd = repl[0]
        
        if not request_message:
            conn.close()
            break
        if(u.role == Role.Advisor):
            match cmd:
                # The Advisor queries for the Situations
                case "sit":
                    conn.send(get_situation().encode())
                case "ans":
                    if sit_id in situations.keys():
                        conn.send("Write a prompt:".encode())
                        msg = Message(u,conn.recv(MESSAGE_SIZE).decode())
                        situations[sit_id].answers.append(msg)
                        conn.send("Reply sent.".encode())
                case _:
                    conn.send(f"Unknown Command {request_message.decode()}".encode())
        else:
            match request_message.decode():
                case "ask":
                    conn.send("Write a prompt:".encode())
                    msg = Message(u,conn.recv(MESSAGE_SIZE).decode())
                    sit = Situation(sit_count, u, msg)
                    sit_count += 1
                    situations[sit.id] = sit
                    conn.send("Situation created, waiting for advice.".encode())
                case "sit":
                    conn.send(get_situation(u).encode())
                case "chk":
                    if sit_id in situations.keys() and situations.get(sit_id).advisee.id == u.id:
                        conn.send("\n".join([str(sit) for sit in situations.get(sit_id) if sit.advisee.id == u.id]))
                case _:
                    conn.send(f"Unknown Command {request_message.decode()}".encode())     

if __name__ == "__main__":
    sock = create_server(("localhost", 12000))
    while True:
        conn, _ = sock.accept()
        u = User(assign_name().encode(), assign_role(), conn)
        users[u.role].append(u)
        conn.send(f"Hello {(u.id).decode()}, you are an {u.role}".encode())
        _thread.start_new_thread(client, (conn, u))