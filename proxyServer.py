import httpSocketServer
import socket
import shared

BUFFERSIZE = 4096

def new_client(headers):
    _id = headers["Clientid"]

    data, host = shared.decrypt_and_decode(server.receive(_id))

    print(str(host))
    HOST = "ifconfig.me"
    PORT = 443

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while True:
            print("Sending to remote (fetched from client): " + str(data))
            s.send(data)
            resp = s.recv(BUFFERSIZE)
            print("---------------------")
            print("Got from remote, echoing back: " + str(resp))
            server.send(_id, shared.encrypt_and_encode_reply(resp))
            print("Echoed back")

            data, host = shared.decrypt_and_decode(server.receive(_id))

server = httpSocketServer.HttpSocketServer("0.0.0.0", 1082, new_client)