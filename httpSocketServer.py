from flask import Flask, request
from dataclasses import dataclass
from random import choice
import shared
import time
from threading import *

def gen_id():
    out = ""
    for i in range(1, 8):
        out += choice(range(100000, 999999))

    return out[:-2]

@dataclass
class Packet():
    clientid: str
    connectionid: str
    content: str
    order: int

class httpSocketServer():
    def __init__(self, callback):
        self.packetsToSend = []
        self.packetsRecvd = []
        self.clients = []
        self.sendOrders = {}
        # approx 5 meg
        self.MAX_PACKET_SIZE = 1250000
        self.callback = callback

        app = Flask(__name__)

        @app.route("/send", methods=["POST"])
        def receive():
            clientid = request.headers.get("clientid")
            connectionid = request.headers.get("connectionid")
            connectionOrder = request.headers.get("connectionorder")
            content = shared.str_to_bytes(request.data)

            self.packetsRecvd.append(Packet(clientid, connectionid, content, connectionOrder))

            return 200

        @app.route("/recieve", methods=["GET"])
        def send():
            clientid = request.headers.get("clientid")
            toSend = ""
            startTime = time.time()
            while toSend == "":
                for i in self.packetsToSend:
                    if i.clientid == clientid:
                        converted = shared.bytes_to_str(i.content) + "PACK_INFO_START" + i.connectionid + "PACK_INFO_END"

                        if len(toSend + converted) > self.MAX_PACKET_SIZE:
                            break

                        toSend += converted

                if toSend == "" and startTime + 15 < time.time():
                    break

            if toSend == "":
                return "RESEND", 200

            return toSend

        @app.route("/connect", methods=["POST"])
        def connect():
            connectionID = request.headers.get("connid")
            clientID = request.headers.get("clientid")
            self.sendOrders[connectionID] = 0
            Thread(target=self.callback, args=(connectionID, clientID))

            return 200

    def receive(self, connectionid):
        lowest = None
        lowestNum = 999999999999
        for i in self.packetsRecvd:
            if i.connectionid == connectionid:
                if lowestNum > i.order:
                    lowestNum = i.order
                    lowest = i

        return lowest.content

    def send(self, clientid, connectionid, content):
        self.sendOrders[connectionid] += 1
        self.packetsToSend.append(Packet(clientid, connectionid, content, self.sendOrders[connectionid]))