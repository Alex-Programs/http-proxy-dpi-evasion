import httpSocketClient
import socket

import shared

REMOTE = "127.0.0.1:1082"
HOST = "0.0.0.0"
PORT = 1085
BUFFERSIZE = 4096

client = httpSocketClient.HttpSocketClient(REMOTE)

client.connect()

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

    while True:
        data = conn.recv(BUFFERSIZE)

        print("Got data back: " + str(data))

        # now send this over to be echoed

        client.send(shared.encrypt_and_encode(host, data))

        resp = shared.decrypt_and_decode_reply(client.receive())

        print("---------------------------------------------------")

        print("Got resp back: " + str(resp))

        conn.send(resp)

        print("Sent resp, waiting")