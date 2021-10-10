import httpSocketServer
import socket
from threading import *
import shared
import time

BUFFERSIZE = 4096

def new_client(headers):
    _id = headers["Clientid"]

    data, host = shared.decrypt_and_decode(server.receive(_id))

    print(str(host))

    HOST = host.split(":")[0]
    PORT = int(host.split(":")[1])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        def outwards_proxy(_id, s):
            print("Outwards proxy started")
            while True:
                data, host = shared.decrypt_and_decode(server.receive(_id))
                if len(data) == 0:
                    print("ERR: DATA TO SHORT: ABORT")
                    break

                print("Sending data from client to remote: " + str(data))
                s.send(data)

        def inwards_proxy(_id, s):
            print("Inwards proxy started")
            while True:
                resp = s.recv(BUFFERSIZE)
                if len(resp) == 0:
                    print("ERR: DATA TO SHORT: ABORT")
                    break

                print("Sending data from remote to client: " + str(resp))
                server.send(_id, shared.encrypt_and_encode_reply(resp))

        Thread(target=inwards_proxy, args=(_id, s)).start()
        Thread(target=outwards_proxy, args=(_id, s)).start()

        #got this earlier; we have to send this along
        s.send(data)

        while True:
            time.sleep(1)


server = httpSocketServer.HttpSocketServer("0.0.0.0", 1082, new_client)