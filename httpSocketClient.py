# see httpsocketserver for an explanation of the cursed transport system
import requests
from dataclasses import dataclass
from random import *
import time
from threading import *

@dataclass()
class ReceiveItem():
    order: int
    data: str

def generate_client_id():
    output = ""
    for i in range(1, 5):
        output += str(choice(range(100 * 10000, 999 * 10000))) + ":"

    output = output[:-2]
    return output

class HttpSocketClient():
    def __init__(self, remote_host):
        self.sendOrder = 0
        self.clientID = generate_client_id()
        self.remote = remote_host
        self.receivedData = []
        self.recvQueueSize = 0
        Thread(target=self.receive_loop).start()

    def send(self, data):
        self.sendOrder += 1
        r = requests.post("http://" + self.remote + "/send", headers={
            "clientid": self.clientID,
            "order": str(self.sendOrder)
        }, data=data)

    def receive_req(self):
        r = requests.get("http://" + self.remote + "/receive", headers={
            "clientid": self.clientID
        }, timeout=15)

        if r.status_code == 200:
            self.recvQueueSize = int(r.headers["queue-size"])
            self.receivedData.append(ReceiveItem(int(r.headers["order"]), r.content))

    def receive_loop(self):
        while True:
            Thread(target=self.receive_req).start()

            time.sleep(0.5)

    def receive(self):
        while True:
            lowest = None
            lowestOrder = 9999999
            for item in self.receivedData:
                if item.order < lowestOrder:
                    lowest = item
                    lowestOrder = item.order

            if lowest:
                self.receivedData.remove(lowest)
                return lowest.data

            time.sleep(0.01)

    def connect(self):
        r = requests.post("http://" + self.remote + "/connect", headers={
            "clientid" : self.clientID
        })

if __name__ == "__main__":
    client = HttpSocketClient("127.0.0.1:1081")

    client.connect()
    client.send("Hello")

    print(str(client.receive()))