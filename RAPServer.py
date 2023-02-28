from __future__ import annotations
from socket import create_server
from threading import Semaphore
from logic import User, Role, Situation, Message, MESSAGE_SIZE
import random
import _thread

users: dict[Role, list[User]] = {Role.Advisee: [], Role.Advisor: []}
"""Dict of users and their roles, key -> Role, value -> list of users in that role"""
situations: list[Situation] = []
"""List of situations"""

sit_sem = Semaphore()
user_sem = Semaphore()

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


def get_situations() -> Situation:
    for sit in situations:
        if sit.advisor is None:
            return sit


def advisor(u: User) -> None:
    """
    Advisor specific function
    :param u:
    :return:
    """
    try:
        global sit_sem
        conn = u.sock
        conn.send(f"Hello {u.id.decode()}, you are an {u.role}\n".encode())

        sit_sem.acquire()
        sit = get_situations()
        if sit is None:
            conn.send("Waiting for situation...\n".encode())
            print(f"Situation count: {len(situations)}")
            while sit is None:
                sit = get_situations()
        conn.send("Found situation\n".encode())
        sit.advisor = u
        sit_sem.release()

        conn.send(f"Advisee: {sit.advisee.id.decode()} asked:\n{sit.message}\n\nWrite a prompt:".encode())

        ans = conn.recv(MESSAGE_SIZE).decode()

        sit.answer = ans

        conn.send("Do you want to continue? (y/n, default y)".encode())
        repl = conn.recv(MESSAGE_SIZE).decode()
        if repl in ["n", "no", "No", "nO", "NO"]:
            disconnect_user(u)
            return

        u = assign_role_to_user(u)
        if u.role == Role.Advisee:
            advisee(u)
        else:
            advisor(u)

    except BrokenPipeError:
        disconnect_user(u)
        return


def disconnect_user(user: User) -> None:
    """
    Disconnects users, by removing them from lists of users and closing the socket

    :param user:
    :return:
    """
    global user_sem
    user.sock.close()
    user_sem.acquire()
    if user in users.values():
        users[user.role].remove(user)
    user_sem.release()
    for sit in situations:
        if sit.advisee == user:
            situations.remove(sit)
    print(f"User {user.id.decode()} disconnected from the server.")


def advisee(u: User) -> None:
    """
    Advisee specific function
    :param u:
    :return:
    """
    try:
        conn = u.sock
        conn.send(f"Hello {u.id.decode()}, you are an {u.role}\nWrite a prompt:\n".encode())
        msg = Message(u, conn.recv(MESSAGE_SIZE).decode())
        sit = Situation(u, msg)
        situations.append(sit)

        print(f"Added a new situation, situation count: {len(situations)}")

        conn.send(f"Waiting for answer...\n".encode())
        while True:
            if sit.answer is None:
                continue
            conn.send(f"Advisor: {sit.advisor.id.decode()} answered:\n{sit.answer}\n".encode())
            conn.send("Do you want to continue? (y/n, default y)".encode())
            repl = conn.recv(MESSAGE_SIZE).decode()
            if repl in ["n", "no", "No", "nO", "NO"]:
                disconnect_user(u)
                return
            u = assign_role_to_user(u)
            if u.role == Role.Advisee:
                advisee(u)
            else:
                advisor(u)
    except BrokenPipeError:
        disconnect_user(u)
        return


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


def assign_role_to_user(user: User) -> User:
    global user_sem
    user_sem.acquire()
    if user in users.values():
        users[user.role].remove(user)
    user.role = assign_role()
    users[user.role].append(user)
    user_sem.release()
    return user


def main():
    sock = create_server(("localhost", 12000))

    print("Server started!")
    print("Waiting for clients...")

    sock.listen(5)
    while True:
        user = assign_role_to_user(User(assign_name().encode(), None, sock.accept()[0]))

        print(f"User {user.id.decode()} connected to the server.")
        users[user.role].append(user)
        _thread.start_new_thread(advisee if user.role == Role.Advisee else advisor, (user,))


if __name__ == "__main__":
    main()
