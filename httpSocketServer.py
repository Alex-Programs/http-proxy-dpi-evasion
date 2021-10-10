# Very cursed. I love it.
# Sending is simple: Send to a endpoint.
# Receiving: Request from an endpoint. It'll slow poll for max x seconds until it either returns data or tells you to rerun the req

from flask import Flask, request
from dataclasses import dataclass
import time
from threading import *

@dataclass()
class SendItem():
    clientid: str
    data: str
    order: int

@dataclass()
class ReceiveItem():
    clientid: str
    data: str
    order: int

class HttpSocketServer():
    def __init__(self, host, port):
        self.app = Flask(__name__)
        self.clients = []

        self.recvBuffs = []
        self.sendBuffs = []
        self.sendOrders = {}

        self.host = host
        self.port = port

        @self.app.route("/send", methods=["POST"])
        def route_receive_data():
            #TODO clientid, data should be in the encrypted segment
            self.recvBuffs.append(ReceiveItem(request.headers["clientid"], request.get_data(), int(request.headers["order"])))
            return "200", 200

        @self.app.route("/receive", methods=["GET"])
        def route_send_data():
            times_looped = 0
            #TODO clientid, data should be in the encrypted segment

            starttime = time.time()
            while True:
                times_looped += 1

                lowest = None
                lowestAmount = 9999999
                for buff in self.sendBuffs:
                    if buff.clientid == request.headers["clientid"] and buff.order < lowestAmount:
                        lowestAmount = buff.order
                        lowest = buff

                if lowest:
                    #TODO encryption
                    self.sendBuffs.remove(lowest)
                    return lowest.data

                if (time.time() - starttime) > 10:
                    return "RESEND", 512

                time.sleep(0.005 + (0.002 * times_looped))

        Thread(target=self.run).start()

    def run(self):
        self.app.run(host=self.host, port=self.port, threaded=True)

    def send(self, clientid, data):
        if not self.sendOrders.get(clientid):
            self.sendOrders[clientid] = 0

        self.sendOrders[clientid] += 1
        order = self.sendOrders[clientid]
        self.sendBuffs.append(SendItem(clientid, data, order))

    def receive(self, clientid):
        while True:
            lowestIndex = 9999999999999
            lowestElement = None
            for buff in self.recvBuffs:
                if buff.clientid == clientid and buff.order < lowestIndex:
                    lowestIndex = buff.order
                    lowestElement = buff

            if lowestElement:
                self.recvBuffs.remove(lowestElement)
                return lowestElement

            else:
                time.sleep(0.01)

if __name__ == "__main__":
    server = HttpSocketServer("0.0.0.0", 1082)
    print("PAST")
    print(str(server.receive("TEST-ID-THING")))
    server.send("TEST-ID-THING", "this is a response test")