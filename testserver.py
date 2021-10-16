from flask import Flask
from waitress import serve

app = Flask(__name__)

class shared:
    count = 0

@app.route("/")
def index():
    shared.count += 1
    if shared.count % 100 == 0:
        print(str(shared.count))

    return "Hello" * 10000


serve(app, host="0.0.0.0", port=8001)
