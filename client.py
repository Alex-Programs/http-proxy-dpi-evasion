from flask import Flask, request, Response
import json
import requests
from shared import *

HOST = "0.0.0.0"
PORT = 1086

REMOTE_HOST = "http://127.0.0.1:8042"

app = Flask(__name__)

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

# act as a normal http proxy receiver, except encode into a encrypted format and send on to the server to then act as a proxy... almost a double proxy

@app.route("/<path:url>", methods=HTTP_METHODS)
@app.route("/p/<path:url>", methods=HTTP_METHODS)
def _proxy(url):
    payload = encrypt(json.dumps({"method": request.method,
                                  "url": "https://" + url,
                                  "headers": dict(request.headers),
                                  "cookies": request.cookies
                                  }))

    resp = requests.get(REMOTE_HOST, headers={"payload": payload})

    if resp.status_code != 200:
        return "PROXY FAILURE", 4242

    resp_payload = json.loads(decrypt(resp.content))

    return Response(resp_payload["content"], resp_payload["status"], resp_payload["headers"])


app.run(host=HOST, port=PORT)
