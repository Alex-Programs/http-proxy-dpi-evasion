from flask import Flask, request, Response
import json
import requests
from shared import *

HOST = "0.0.0.0"
PORT = 8042

app = Flask(__name__)

# act as a normal http proxy receiver, except encode into a encrypted format and send on to the server to then act as a proxy... almost a double proxy
@app.route("/")
def index():
    data = json.loads(decrypt(request.headers["payload"]))

    print(str(data))

    resp = requests.request(
        method=data["method"],
        url=data["url"],
        headers=data["headers"],
        data=data["data"],
        cookies=data["cookies"]
    )

    return encrypt(json.dumps({
        "content": resp.content,
        "status": resp.status_code,
        "headers": resp.headers,
    }))

app.run(host=HOST, port=PORT)