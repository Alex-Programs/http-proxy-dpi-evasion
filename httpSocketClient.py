import requests
from dataclasses import dataclass
import time
from threading import *
import shared


@dataclass
class Packet():
    connectionid: str
    content: str
    order: int

def parse_packets(data):
    packets = data.split("PACK_INFO_END")
    out = []
    for packet in packets:
        splitted = packet.split("PACK_INFO_START")
        data = shared.str_to_bytes(splitted[0])
        splitted = splitted.split("||||||||")
        order = splitted[0]
        connid = splitted[1]

        out.append(Packet(connid, data, order))

class httpSocketClient():
    def __init__(self, host):
        self.host = host
        self.packetsRecvd = []
        self.clientid = shared.gen_id()
        self.sendOrder = 0
        self.create_recv_threads()

    def gen_id(self):
        return shared.gen_id()

    def create_recv_threads(self):
        for i in range(1, 5):
            Thread(target=self.recv_thread).start()

    def recv_thread(self):
        while True:
            r = requests.get(self.host + "/receive", headers={"clientid": self.clientid})

            if r.content.decode("utf8") == "RESEND":
                continue

            self.packetsRecvd.append(parse_packets(r.content))
            print(str(self.packetsRecvd))

    def receive(self, connid):
        lowest = None
        lowestI = 9999999999
        while not lowest:
            for i in self.packetsRecvd:
                if i.connectionid == connid and i.order < lowestI:
                    lowestI = i.order
                    lowest = i

        return lowest

    def send(self, connid, data):
        self.sendOrder += 1

        r = requests.post(self.host + "/send", data=shared.bytes_to_str(data), headers={
            "clientid": self.clientid,
            "connectionid": connid,
            "connectionorder": str(self.sendOrder)
        })

    def connect(self):
        connid = self.gen_id()

        r = requests.post(self.host + "/connect", headers={
            "connid": connid,
            "clientid": self.clientid
        })

        return connid

if __name__ == "__main__":
    client = httpSocketClient("http://127.0.0.1:1082")

    connid = client.connect()

    client.send(connid, bytes("Hello", "utf8"))

    print(str(client.receive(connid)))