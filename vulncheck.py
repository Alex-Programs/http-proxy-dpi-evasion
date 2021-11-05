# checks if the firewall is susceptible to stateless smuggling
import socket
import flask

def sock_listen():
    HOST = "0.0.0.0"
    PORT = 80

    respData = """HTTP/1.1 200 OK
Content-Length: 12
Connection: close
Content-Type: text/html

Hello world!""".encode("utf8")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))

        while True:
            s.listen()

            conn, addr = s.accept()

            conn.send(respData)
            conn.send(respData)

            conn.close()

sock_listen()