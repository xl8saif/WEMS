import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

from werkzeug.serving import make_server


def _runtime_dir():
    """Return a writable directory beside the executable when frozen."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _write_log(message):
    try:
        log_path = _runtime_dir() / "wems-launcher.log"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(message.rstrip() + "\n")
    except Exception:
        pass


def main():
    # Keep relative application data (database, invoices, backups, exports)
    # beside the portable WEMS executable.
    os.chdir(_runtime_dir())
    _write_log(f"Starting WEMS; cwd={Path.cwd()}; frozen={getattr(sys, 'frozen', False)}")

    try:
        from app import app
    except Exception as exc:
        _write_log(f"Application import failed: {type(exc).__name__}: {exc!r}")
        raise

    host = "127.0.0.1"
    port = 5000

    try:
        server = make_server(host, port, app, threaded=True)
    except Exception as exc:
        _write_log(f"Server creation failed: {type(exc).__name__}: {exc!r}")
        raise

    thread = threading.Thread(target=server.serve_forever, name="WEMS-HTTP", daemon=True)
    thread.start()
    _write_log(f"HTTP server thread started on http://{host}:{port}/")

    # Give the server a short window to become responsive before opening the
    # browser. This also avoids launching a browser against a dead startup.
    ready = False
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if not thread.is_alive():
            _write_log("HTTP server thread exited unexpectedly during startup.")
            raise RuntimeError("WEMS HTTP server stopped during startup.")
        try:
            import socket
            with socket.create_connection((host, port), timeout=0.5):
                ready = True
                break
        except OSError:
            time.sleep(0.2)

    if not ready:
        _write_log("HTTP server did not become ready within 15 seconds.")
        server.shutdown()
        raise RuntimeError("WEMS HTTP server did not become ready.")

    _write_log("HTTP server is ready; opening browser.")
    webbrowser.open(f"http://{host}:{port}/")

    try:
        while thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        _write_log("KeyboardInterrupt received; shutting down WEMS.")
    finally:
        server.shutdown()
        thread.join(timeout=5)
        _write_log("WEMS server stopped.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _write_log(f"Fatal WEMS launcher error: {type(exc).__name__}: {exc!r}")
        raise
