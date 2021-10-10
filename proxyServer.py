import httpSocketServer
import socket
from threading import *
import shared
import time
from random import choice

class TimeoutShared():
    timeoutIDS = []

BUFFERSIZE = 4096

def new_client(headers):
    _id = headers["Clientid"]

    received = server.receive(_id)
    if received == "TIMEOUT":
        return
    data, host = shared.decrypt_and_decode(received)

    HOST = host.split(":")[0]
    PORT = int(host.split(":")[1])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(120)
        s.connect((HOST, PORT))

        def outwards_proxy(_id, s, timeoutID):
            while True:
                received = server.receive(_id)

                if received == "TIMEOUT":
                    print("ABORT DUE TO TIMEOUT")
                    TimeoutShared.timeoutIDS.append(timeoutID)
                    server.rmclient(_id)
                    break

                data, host = shared.decrypt_and_decode(received)
                if len(data) == 0:
                    print("ERR: DATA TO SHORT: ABORT")
                    TimeoutShared.timeoutIDS.append(timeoutID)
                    server.rmclient(_id)
                    break

                s.send(data)

        def inwards_proxy(_id, s, timeoutID):
            while True:
                try:
                    resp = s.recv(BUFFERSIZE)
                except socket.timeout:
                    print("ERR: TIMEOUT")
                    TimeoutShared.timeoutIDS.append(timeoutID)
                    server.rmclient(_id)
                    break

                if len(resp) == 0:
                    print("ERR: DATA TO SHORT: ABORT")
                    TimeoutShared.timeoutIDS.append(timeoutID)
                    server.rmclient(_id)
                    break

                server.send(_id, shared.encrypt_and_encode_reply(resp))

        timeoutID = choice(range(1, 9999999999999))

        Thread(target=inwards_proxy, args=(_id, s, timeoutID)).start()
        Thread(target=outwards_proxy, args=(_id, s, timeoutID)).start()

        #got this earlier; we have to send this along
        s.send(data)

        while True:
            time.sleep(5)
            if timeoutID in TimeoutShared.timeoutIDS:
                print("Exiting due to timeout")
                break


server = httpSocketServer.HttpSocketServer("0.0.0.0", 1082, new_client)