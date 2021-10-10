import httpSocketClient
import socket
from threading import *
import time

import shared

REMOTE = "127.0.0.1:1082"
HOST = "0.0.0.0"
PORT = 1085
BUFFERSIZE = 4096

client = httpSocketClient.HttpSocketClient(REMOTE)

client.connect()


def loop_local_to_remote(local_sock, host):
    while True:
        data = local_sock.recv(BUFFERSIZE)
        print("\n\n\n\n\nLOCAL_TO_REMOTE: " + str(data))
        client.send(shared.encrypt_and_encode(host, data))


def loop_remote_to_local(local_sock, host):
    while True:
        data = shared.str_to_bytes(client.receive())
        print("\n\n\n\n\nREMOTE_TO_LOCAL: " + str(data))
        local_sock.send(data)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    while True:
        try:
            s.bind((HOST, PORT))
            print("Bound at " + str(PORT))
            break
        except:
            PORT += 1

    s.listen()
    conn, addr = s.accept()

    initial_data = conn.recv(BUFFERSIZE)

    print(str(initial_data))

    initial_data = initial_data.decode("utf8")

    print(str(initial_data))

    host = initial_data.split(" ")[1]

    conn.send("HTTP/1.1 200 OK\n\n".encode("utf8"))

    print("Responded")

    Thread(target=loop_local_to_remote, args=(conn, host)).start()
    Thread(target=loop_remote_to_local, args=(conn, host)).start()

    while True:
        time.sleep(1)