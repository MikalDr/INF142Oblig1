from socket import socket
from logic import MESSAGE_SIZE, SERVER_DISCONNECT_COMMAND
import _thread
import sys


CONNECTED_TO_SERVER = False

def server_response(sock: socket) -> None:
    """
    Prints server response
    :param sock:
    :return:
    """
    global CONNECTED_TO_SERVER
    while True:
        msg = sock.recv(MESSAGE_SIZE).decode()
        if msg in SERVER_DISCONNECT_COMMAND:
            CONNECTED_TO_SERVER = False
            sys.exit()
        print(msg)


def main():
    global CONNECTED_TO_SERVER
    sock = socket()
    sock.connect(("localhost", 12000))
    CONNECTED_TO_SERVER = True
    _thread.start_new_thread(server_response, (sock,))
    while CONNECTED_TO_SERVER:
        cmd = input()
        sock.sendall(cmd.encode())
    sock.close()

if __name__ == "__main__":
    main()
