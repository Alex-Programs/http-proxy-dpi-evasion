import requests
from threading import *

def send():
    r = requests.get("http://172.29.56.44:8001")

while True:
    Thread(target=send).start()