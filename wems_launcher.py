import os
import sys
import threading
import time
import traceback
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
            handle.flush()
    except Exception:
        pass


def main():
    runtime_dir = _runtime_dir()
    os.chdir(runtime_dir)

    # Packaged resources are read from PyInstaller's internal directory, while
    # mutable application data must live beside the portable executable.
    os.environ.setdefault("WEMS_DATA_DIR", str(runtime_dir))
    _write_log(
        f"Starting WEMS; cwd={Path.cwd()}; frozen={getattr(sys, 'frozen', False)}; "
        f"meipass={getattr(sys, '_MEIPASS', '')}; data_dir={os.environ.get('WEMS_DATA_DIR')}"
    )

    try:
        from app import app
        _write_log("Application import succeeded.")
    except Exception as exc:
        _write_log(f"Application import failed: {type(exc).__name__}: {exc!r}")
        _write_log(traceback.format_exc())
        raise

    host = "127.0.0.1"
    port = 5000

    try:
        server = make_server(host, port, app, threaded=True)
        _write_log(f"HTTP server created on http://{host}:{port}/")
    except Exception as exc:
        _write_log(f"Server creation failed: {type(exc).__name__}: {exc!r}")
        _write_log(traceback.format_exc())
        raise

    thread = threading.Thread(target=server.serve_forever, name="WEMS-HTTP", daemon=True)
    thread.start()
    _write_log("HTTP server thread started.")

    ready = False
    deadline = time.monotonic() + 30
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
        _write_log("HTTP server did not become ready within 30 seconds.")
        server.shutdown()
        raise RuntimeError("WEMS HTTP server did not become ready.")

    _write_log("HTTP server is ready; opening browser.")
    try:
        webbrowser.open(f"http://{host}:{port}/")
    except Exception as exc:
        _write_log(f"Browser launch warning: {type(exc).__name__}: {exc!r}")

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
        _write_log(traceback.format_exc())
        raise
