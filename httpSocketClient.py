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
    return "TEST-ID-THING"
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
        Thread(target=self.receive_loop).start()

    def send(self, data):
        self.sendOrder += 1
        r = requests.post("http://" + self.remote + "/send", headers={
            "clientid": self.clientID,
            "order": str(self.sendOrder)
        }, data=data)

    def receive_loop(self):
        receiveOrder = 0

        while True:
            r = requests.get("http://" + self.remote + "/receive", headers={
                "clientid": self.clientID
            }, timeout=15)

            if r.status_code == 200:
                receiveOrder += 1

                self.receivedData.append(ReceiveItem(receiveOrder, r.content))

    def receive(self):
        while True:
            lowest = None
            lowestOrder = 9999999
            for item in self.receivedData:
                if item.order < lowestOrder:
                    lowest = item
                    lowestOrder = item.order

            if lowest:
                print(str(self.receivedData))
                self.receivedData.remove(lowest)
                return lowest.data

            time.sleep(0.01)

if __name__ == "__main__":
    client = HttpSocketClient("127.0.0.1:1082")

    client.send("Hello")

    print(str(client.receive()))