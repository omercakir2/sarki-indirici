"""Runtime paths and settings, all overridable with environment variables."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

APP_NAME = "Bedava ve Reklamsız MP3 Şarkı İndirici"
APP_SLUG = "SarkiIndirici"

SYSTEM = platform.system()  # "Darwin", "Windows", "Linux"
FROZEN = getattr(sys, "frozen", False)  # True inside the PyInstaller desktop build
IN_DOCKER = os.environ.get("SARKI_IN_DOCKER") == "1" or Path("/.dockerenv").exists()


def _default_data_dir() -> Path:
    home = Path.home()
    if SYSTEM == "Darwin":
        return home / "Library" / "Application Support" / APP_SLUG
    if SYSTEM == "Windows":
        return Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local")) / APP_SLUG
    return Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share")) / "sarki-indirici"


def _default_download_dir() -> Path:
    return Path.home() / "Downloads" / "Sarki-Indirici"


DATA_DIR = Path(os.environ.get("SARKI_DATA_DIR", _default_data_dir()))
DOWNLOAD_DIR = Path(os.environ.get("SARKI_DOWNLOAD_DIR", _default_download_dir()))

# Directory holding bundled helper binaries (ffmpeg, ffprobe, deno).
# In the desktop build PyInstaller unpacks them to <_MEIPASS>/bin.
if FROZEN:
    BUNDLED_BIN_DIR: Path | None = Path(getattr(sys, "_MEIPASS")) / "bin"
elif os.environ.get("SARKI_BIN_DIR"):
    BUNDLED_BIN_DIR = Path(os.environ["SARKI_BIN_DIR"])
else:
    BUNDLED_BIN_DIR = None

# Built frontend (Vite output). Desktop build bundles it under <_MEIPASS>/web.
if FROZEN:
    WEB_DIR = Path(getattr(sys, "_MEIPASS")) / "web"
else:
    WEB_DIR = Path(
        os.environ.get("SARKI_WEB_DIR", Path(__file__).resolve().parents[2] / "frontend" / "dist")
    )

MAX_PARALLEL = int(os.environ.get("SARKI_MAX_PARALLEL", "2"))
AUTO_UPDATE = os.environ.get("SARKI_AUTO_UPDATE", "1") != "0"

# Opening a folder only makes sense when the server runs on the user's own desktop.
CAN_OPEN_FOLDER = not IN_DOCKER and os.environ.get("SARKI_CAN_OPEN_FOLDER", "1") != "0"
