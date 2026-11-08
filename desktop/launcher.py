"""Desktop entry point: run the FastAPI app on a free local port and show it
in a native window (pywebview). Falls back to the default browser if no
webview is available."""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path


def _redirect_output(data_dir: Path) -> None:
    """Windowed builds have no console; keep a log file instead."""
    data_dir.mkdir(parents=True, exist_ok=True)
    log = open(data_dir / "app.log", "w", encoding="utf-8", buffering=1)
    sys.stdout = log
    sys.stderr = log


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_until_up(url: str, timeout: float = 30) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(url + "/api/status", timeout=1)
            return True
        except Exception:
            time.sleep(0.15)
    return False


def main() -> None:
    from app import config  # noqa: E402  (after PyInstaller has set up paths)

    if getattr(sys, "frozen", False) or sys.stdout is None:
        _redirect_output(config.DATA_DIR)

    import uvicorn

    from app.main import app

    port = int(os.environ.get("SARKI_PORT") or _free_port())
    url = f"http://127.0.0.1:{port}"
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", log_config=None)
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    _wait_until_up(url)

    try:
        import webview

        webview.create_window(
            config.APP_NAME,
            url,
            width=1120,
            height=860,
            min_size=(420, 640),
            background_color="#0f1612",
        )
        webview.start()
    except Exception as exc:  # no WebView2 / WebKit available
        print(f"webview unavailable ({exc}); opening browser", flush=True)
        webbrowser.open(url)
        try:
            while thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    finally:
        server.should_exit = True
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
