import json
import time

from websocket import create_connection


class WebSocket:
    def __init__(self, url, payload):
        self.url = url
        self.payload = payload
        self.websocket = None

    def connect(self, token_trader):
        self.websocket = create_connection(self.url)
        self.__create_session(token_trader)
        self.__action(self.payload)

    def __create_session(self, token_trader):
        # TODO GET auth token
        payload = json.dumps({
            "q": "v1/broker.oms/createSession",
            "sid": 13,
            "d": {
                "token": token_trader
            }
        })
        self.websocket.send(payload)

    def __action(self, payload):
        time.sleep(1)
        self.websocket.send(json.dumps(payload))

    def close(self):
        self.websocket.close()
