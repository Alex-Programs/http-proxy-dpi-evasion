# Very cursed. I love it.
# Sending is simple: Send to a endpoint.
# Receiving: Request from an endpoint. It'll slow poll for max x seconds until it either returns data or tells you to rerun the req

from flask import Flask, request
from dataclasses import dataclass
import time
from threading import *
from waitress import serve

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
    def __init__(self, host, port, connectCallback):
        self.connectCallback = connectCallback

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

        @self.app.route("/connect", methods=["POST"])
        def connect():
            Thread(target=self.connectCallback, args=(dict(request.headers),)).start()
            return "OK-maybe, this is a huge bodge", 200

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
        #serve(self.app, host=self.host, port=self.port)
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
                return lowestElement.data

            else:
                time.sleep(0.01)

if __name__ == "__main__":
    def new_client(headers):
        print("Client func running")
        print(str(server.receive(headers["Clientid"])))
        server.send(headers["Clientid"], "this is a response test")

    server = HttpSocketServer("0.0.0.0", 1082, new_client)