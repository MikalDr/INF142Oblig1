from __future__ import annotations
from socket import create_server
from logic import User, Role, Situation, Message
import random
import _thread

MESSAGE_SIZE = 1024
"""Message size, in bytes"""
sit_count = 0
"""Situation ID"""
users: dict[Role: list[User]] = {Role.Advisee: [], Role.Advisor: []}
"""Dict of users and their roles, key -> Role, value -> list of users in that role"""
situations: dict[int: Situation] = {}
"""Situations, key -> situation ID, value -> Situation"""

with open("animals.txt", "r") as f:
    animals = f.read().splitlines()

with open("adjectives.txt", "r") as f:
    adjectives = f.read().splitlines()


def assign_name() -> str:
    """
    Returns a randomly generated name, ensuring anonymity.
    :return:
    """
    return random.choice(adjectives) + "" + random.choice(animals)


def assign_role() -> Role:
    """
    Returns either an advisee or advisor.
    If there are no advisee's, returns an Advisee, else, randomly chooses
    :return:
    """
    if len(users.get(Role.Advisee)) == 0:
        return Role.Advisee
    else:
        return random.choice([Role.Advisee, Role.Advisor])


def get_situation(u=None) -> str:
    """
    Parses the situation dict into a string format.
    If a user is given, only situations that have the same id as the given users are returned.
    :param u:
    :return:
    """
    return "\n".join([str(sit) for sit in situations.values()]) if u is None else "\n".join(
        [str(sit) for sit in situations.values() if sit.advisee.id == u.id])


def advisor_cmd() -> str:
    """
    Returns advisor commands
    :return:
    """
    return "sit: Shows list of all open situations" \
           "ans {sid_id}: Answers the specified situation"


def advisor(u: User) -> None:
    """
    Advisor specific function
    :param u:
    :return:
    """
    global sit_count
    conn = u.sock
    print(f"User {u.id.decode()} connected to the server.")
    conn.send(f"Hello {u.id.decode()}, you are an {u.role}".encode())
    conn.send(f"{advisor_cmd()}".encode())
    while True:
        cmd, sit_id = parse_answer(conn.recv(1024))
        match cmd:
            # The Advisor queries for the Situations
            case "sit":
                conn.send(get_situation().encode())
            case "ans":
                if sit_id in situations.keys():
                    conn.send("Write a prompt:".encode())
                    msg = Message(u, conn.recv(MESSAGE_SIZE).decode())
                    situations[sit_id].answers.append(msg)
                    conn.send("Reply sent.".encode())
            case _:
                conn.send(f"Unknown Command {cmd}".encode())


def advisee(u: User) -> None:
    """
    Advisee specific function
    :param u:
    :return:
    """
    global sit_count
    print(f"User {u.id.decode()} connected to the server.")
    conn = u.sock
    conn.send(f"Hello {u.id.decode()}, you are an {u.role}".encode())
    conn.send("Write a prompt:".encode())
    msg = Message(u, conn.recv(MESSAGE_SIZE).decode())
    sit = Situation(sit_count, u, msg)
    sit_count += 1
    situations[sit.id] = sit


def parse_answer(msg: bytes) -> tuple[str, int]:
    """
    Takes in an answer from the client, and then parses it for use
    :param msg:
    :return:
    """
    repl = msg.decode().split(" ")
    if len(repl) > 1:
        cmd, sit_id = repl
        sit_id = int(sit_id)
    else:
        sit_id = None
        cmd = repl[0]
    return cmd, sit_id


if __name__ == "__main__":
    sock = create_server(("localhost", 12000))

    print("Server started!")
    print("waiting for clients...")

    sock.listen(5)
    while True:
        user = User(assign_name().encode(), assign_role(), sock.accept()[0])
        users[user.role].append(user)
        _thread.start_new_thread(advisee if user.role == Role.Advisee else advisor, (user,))
    sock.close()
