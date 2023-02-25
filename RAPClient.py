from socket import socket


def request_to_server(sock: socket, message: str) -> str:
    sock.sendall(message.encode())
    return sock.recv(1024).decode()

if __name__ == "__main__":
    sock = socket()
    sock.connect(("localhost", 12000))
    print(sock.recv(1024).decode())
    while True:
        cmd = input()
        response = request_to_server(sock, cmd)
        print(response)
        
