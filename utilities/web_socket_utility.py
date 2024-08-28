import threading
import json
from websockets.sync.client import connect
from configs.config import FUTURES
import time


class WebSocketHandler:
    def __init__(self) -> None:
        self.kline_data = {}
        self.id = 1
        self.ws = None
        self.lock = threading.Lock()
        self.keep_running = True
        self.is_connected = False  # To track connection status
        self.subscriptions = []  # Store subscriptions to reapply on reconnect
        t = threading.Thread(target=self.start_ws)
        t1 = threading.Thread(target=self.get_latest_data)
        t.daemon = True
        t1.daemon = True
        t.start()
        t1.start()

    def start_ws(self):
        reconnect_delay = 1
        while self.keep_running:
            try:
                with connect(FUTURES["web_socket"]) as websocket:
                    self.ws = websocket
                    self.is_connected = True
                    print("Connected to WebSocket successfully.")

                    # Reapply subscriptions after reconnecting
                    with self.lock:
                        for subscription in self.subscriptions:
                            self.ws.send(json.dumps(subscription))

                    reconnect_delay = 1  # Reset delay after successful connection
                    while self.keep_running:
                        message = websocket.recv()
                        if message:
                            self.on_message(message)
            except Exception as e:
                print(f"WebSocket error: {e}")
                self.is_connected = False
                time.sleep(reconnect_delay)
                reconnect_delay = min(
                    reconnect_delay * 2, 60
                )  # Exponential backoff up to 60 seconds

    def subscribe(self, symbol: str, interval: str = "5m"):
        payload = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@kline_{interval}"],
            "id": self.id,
        }
        self.subscriptions.append(payload)  # Save the subscription
        self.id += 1

        with self.lock:
            if self.ws is not None and self.is_connected:
                self.ws.send(json.dumps(payload))
            else:
                print("WebSocket is not connected. Subscription queued.")

    def on_message(self, message: str):
        try:
            response = json.loads(message)
            if "k" in response and response["e"] == "kline":
                symbol = response["s"]
                close_price = response["k"]["c"]
                self.kline_data[symbol] = close_price
                print(f"Kline Data: {self.kline_data}")
            else:
                print("Received a message that is not a kline event.")
        except Exception as e:
            print(f"Error processing message: {e}")

    def stop(self):
        self.keep_running = False
        print("WebSocket handler stopped.")

    def data_pulling_loop(self):
        while self.keep_running:
            time.sleep(10)
            latest_data = self.get_latest_data()
            print(f"Pulled data: {latest_data}")

    def get_latest_data(self):
        with self.lock:
            return self.kline_data.copy()
