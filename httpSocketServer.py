from flask import Flask, request
from dataclasses import dataclass
import shared
import time
from threading import *


@dataclass
class Packet():
    clientid: str
    connectionid: str
    content: str
    order: int


class httpSocketServer():
    def __init__(self, host, port, callback):
        self.packetsToSend = []
        self.packetsRecvd = []
        self.clients = []
        self.sendOrders = {}
        # approx 5 meg
        self.MAX_PACKET_SIZE = 1250000

        app = Flask(__name__)

        @app.route("/send", methods=["POST"])
        def receive():
            clientid = request.headers.get("clientid")
            connectionid = request.headers.get("connectionid")
            connectionOrder = request.headers.get("connectionorder")
            content = shared.str_to_bytes(request.data)

            self.packetsRecvd.append(Packet(clientid, connectionid, content, int(connectionOrder)))

            print(str(self.packetsRecvd))

            return "OK", 200

        @app.route("/receive", methods=["GET"])
        def send():
            clientid = request.headers.get("clientid")
            toSend = ""
            startTime = time.time()
            while toSend == "":
                for i in self.packetsToSend:
                    if i.clientid == clientid:
                        print(i.content)
                        converted = str(shared.bytes_to_str(
                            i.content)) + "PACK_INFO_START" + str(i.order) + "||||||||" + str(i.connectionid) + "PACK_INFO_END"

                        if len(toSend + converted) > self.MAX_PACKET_SIZE:
                            break

                        toSend += converted

                if toSend == "" and startTime + 15 < time.time():
                    break

                if toSend == "":
                    time.sleep(0.02)

            if toSend == "":
                return "RESEND", 200

            print("Sending down " + toSend)

            return toSend

        @app.route("/connect", methods=["POST"])
        def connect():
            connectionID = request.headers.get("connid")
            clientID = request.headers.get("clientid")
            self.sendOrders[connectionID] = 0
            Thread(target=callback, args=(connectionID, clientID, self)).start()

            return "OK", 200

        app.run(host=host, port=port)

    def receive(self, connectionid):
        lowest = None
        lowestNum = 999999999999
        while lowest == None:
            for i in self.packetsRecvd:
                if i.connectionid == connectionid:
                    if lowestNum > i.order:
                        lowestNum = i.order
                        lowest = i

            if not lowest:
                time.sleep(0.01)

        return lowest.content

    def send(self, clientid, connectionid, content):
        print(str(self.sendOrders))
        self.sendOrders[connectionid] += 1
        self.packetsToSend.append(Packet(clientid, connectionid, content, self.sendOrders[connectionid]))

if __name__ == "__main__":
    def callback(connid, clientid, server):
        print("Client func running" * 50)
        print(str(server.receive(connid)))
        server.send(clientid, connid, bytes("World", "utf8"))

    server = httpSocketServer("0.0.0.0", 1082, callback)