#!/usr/bin/env python3
"""Desktop launcher for the web frontend + local backend API."""

from __future__ import annotations

import threading
import time
import webbrowser

import uvicorn

from web_backend import app


def run_api() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")


def main() -> None:
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8765")

    try:
        while api_thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
