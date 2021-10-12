import httpSocketClient
import socket
from threading import *
import time

import shared

REMOTE = "127.0.0.1:1081"
HOST = "0.0.0.0"
PORT = 1085
BUFFERSIZE = 4096

def loop_local_to_remote(local_sock, host, client):
    while True:
        try:
            data = local_sock.recv(BUFFERSIZE)
        except ConnectionResetError:
            print("CONNECTION RESET")
            return

        if len(data) == 0:
            print("EMPTY MESSAGE ERR")
            return

        client.send(shared.encrypt_and_encode(host, data))


def loop_remote_to_local(local_sock, client):
    while True:
        data = shared.decrypt_and_decode_reply(client.receive())
        try:
            local_sock.send(data)
        except ConnectionResetError:
            print("CONNECTION RESET")
            return

        except BrokenPipeError:
            print("BROKEN PIPE")
            return

def handle_conn(conn):
    client = httpSocketClient.HttpSocketClient(REMOTE)

    client.connect()

    initial_data = conn.recv(BUFFERSIZE)

    initial_data = initial_data.decode("utf8")

    host = initial_data.split(" ")[1]

    conn.send("HTTP/1.1 200 OK\n\n".encode("utf8"))

    Thread(target=loop_local_to_remote, args=(conn, host, client)).start()
    Thread(target=loop_remote_to_local, args=(conn, client)).start()

    while True:
        time.sleep(1)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    while True:
        try:
            s.bind((HOST, PORT))
            print("Bound at " + str(PORT))
            break
        except:
            PORT += 1

    while True:
        s.listen()

        conn, addr = s.accept()

        Thread(target=handle_conn, args=(conn,)).start()