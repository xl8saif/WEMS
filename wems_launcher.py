import threading
import time
import webbrowser

from werkzeug.serving import make_server

from app import app


class WEMSServer:
    def __init__(self, flask_app, host="127.0.0.1", port=5000):
        self.server = make_server(host, port, flask_app)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self.server.shutdown()


def main():
    host = "127.0.0.1"
    port = 5000
    server = WEMSServer(app, host, port)
    server.start()
    time.sleep(0.8)
    webbrowser.open(f"http://{host}:{port}/")
    try:
        while server.thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
