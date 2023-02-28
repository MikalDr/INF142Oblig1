from socket import socket
from logic import MESSAGE_SIZE
import _thread
import atexit


def server_response(sock: socket) -> None:
    """
    Prints server response
    :param sock:
    :return:
    """
    while True:
        print(sock.recv(MESSAGE_SIZE).decode())


def main():
    sock = socket()
    sock.connect(("localhost", 12000))
    _thread.start_new_thread(server_response, (sock,))
    while True:
        cmd = input()
        sock.sendall(cmd.encode())


def disconnect(sock: socket):
    sock.close()


atexit.register(disconnect, socket)

if __name__ == "__main__":
    main()
