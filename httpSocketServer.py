# Very cursed. I love it.
# Sending is simple: Send to a endpoint.
# Receiving: Request from an endpoint. It'll slow poll for max x seconds until it either returns data or tells you to rerun the req

from flask import Flask, request, Response
from dataclasses import dataclass
import time
from threading import *
from waitress import serve
from numba import jit


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
            self.recvBuffs.append(
                ReceiveItem(request.headers["clientid"], request.get_data(), int(request.headers["order"])))
            print("R" + str(len(self.recvBuffs)))
            return "200", 200

        @self.app.route("/connect", methods=["POST"])
        def connect():
            Thread(target=self.connectCallback, args=(dict(request.headers),)).start()
            return "OK-maybe, this is a huge bodge", 200

        @self.app.route("/receive", methods=["GET"])
        def route_send_data():
            times_looped = 0

            print("S" + str(len(self.sendBuffs)))

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
                    self.sendBuffs.remove(lowest)
                    resp = Response(lowest.data)
                    resp.headers["queue-size"] = len(self.sendBuffs)
                    resp.headers["order"] = lowestAmount

                if (time.time() - starttime) > 10:
                    return "RESEND", 512

                time.sleep(0.005 + (0.002 * times_looped))

        Thread(target=self.run).start()

    def run(self):
        serve(self.app, host=self.host, port=self.port, threads=64)
        # self.app.run(host=self.host, port=self.port, threaded=True)

    def send(self, clientid, data):
        if not self.sendOrders.get(clientid):
            self.sendOrders[clientid] = 0

        self.sendOrders[clientid] += 1
        order = self.sendOrders[clientid]
        self.sendBuffs.append(SendItem(clientid, data, order))

    def receive(self, clientid):
        startTime = time.time()

        print("R" + str(len(self.recvBuffs)))
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

            if (time.time() - startTime) > 300:
                return "TIMEOUT"

    def rmclient(self, _id):
        try:
            self.clients.remove(_id)
        except:
            pass

        try:
            del self.sendOrders[_id]

        except:
            pass

        def shouldnt_rm(order):
            return order.clientid != _id

        try:
            self.sendBuffs = list(filter(shouldnt_rm, self.sendBuffs))
            self.recvBuffs = list(filter(shouldnt_rm, self.recvBuffs))
        except:
            pass


if __name__ == "__main__":
    def new_client(headers):
        print("Client func running")
        print(str(server.receive(headers["Clientid"])))
        server.send(headers["Clientid"], "this is a response test")


    server = HttpSocketServer("0.0.0.0", 1082, new_client)
