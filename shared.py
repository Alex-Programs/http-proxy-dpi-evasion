import json
from base64 import b64decode, b64encode
from random import choice

# this file is an abomination

# it would be really nice if we just worked out a universal url-safe way to send bytes...

#takes data that has been converted to base64, then turned into utf-8
def bytes_to_str(data):
    data = b64encode(data)

    return data.decode("utf8")

#takes data that has been converted to base64, then turned into utf-8
def str_to_bytes(data):
    data = b64decode(data)

    return data

def encrypt_and_encode(host, data):
    return json.dumps(
        {
            "data": bytes_to_str(data),
            "host": host
        }
    )


def decrypt_and_decode(data):
    data = json.loads(data)

    return str_to_bytes(data["data"]), data["host"]


def encrypt_and_encode_reply(data):
    return bytes_to_str(data)


def decrypt_and_decode_reply(data):
    return str_to_bytes(data)

def gen_id():
    out = ""
    for i in range(1, 8):
        out += str(choice(range(100000, 999999))) + ":"

    return out[:-2]