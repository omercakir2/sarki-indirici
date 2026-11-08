"""Download ffmpeg, ffprobe and deno for the current platform into desktop/bin.

Run before PyInstaller:  python desktop/fetch_tools.py
These get bundled into the desktop app so friends need to install nothing.
(yt-dlp is NOT bundled: the app installs and updates it at runtime.)
"""

from __future__ import annotations

import io
import platform
import shutil
import stat
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

DENO_VERSION = "2.9.4"
BIN = Path(__file__).resolve().parent / "bin"

SYSTEM = platform.system()
ARM = platform.machine().lower() in ("arm64", "aarch64")


def fetch(url: str) -> bytes:
    print(f"  get {url}", flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": "sarki-indirici-build"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return resp.read()


def save(name: str, data: bytes) -> None:
    path = BIN / name
    path.write_bytes(data)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"  ok  {path.name} ({len(data) // 1_000_000} MB)", flush=True)


def from_zip(data: bytes, member_suffix: str) -> bytes:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for name in zf.namelist():
            if name.endswith(member_suffix):
                return zf.read(name)
    raise SystemExit(f"{member_suffix} not found in archive")


def main() -> None:
    shutil.rmtree(BIN, ignore_errors=True)
    BIN.mkdir(parents=True)

    if SYSTEM == "Darwin":
        arch = "arm64" if ARM else "amd64"
        base = f"https://ffmpeg.martin-riedl.de/redirect/latest/macos/{arch}/release"
        save("ffmpeg", from_zip(fetch(f"{base}/ffmpeg.zip"), "ffmpeg"))
        save("ffprobe", from_zip(fetch(f"{base}/ffprobe.zip"), "ffprobe"))
        target = "aarch64-apple-darwin" if ARM else "x86_64-apple-darwin"
        save("deno", from_zip(fetch(_deno(target)), "deno"))
    elif SYSTEM == "Windows":
        z = fetch(
            "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/"
            "ffmpeg-master-latest-win64-gpl.zip"
        )
        save("ffmpeg.exe", from_zip(z, "bin/ffmpeg.exe"))
        save("ffprobe.exe", from_zip(z, "bin/ffprobe.exe"))
        save("deno.exe", from_zip(fetch(_deno("x86_64-pc-windows-msvc")), "deno.exe"))
    elif SYSTEM == "Linux":
        arch = "linuxarm64" if ARM else "linux64"
        data = fetch(
            "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/"
            f"ffmpeg-master-latest-{arch}-gpl.tar.xz"
        )
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:xz") as tf:
            for m in tf.getmembers():
                if m.name.endswith(("bin/ffmpeg", "bin/ffprobe")):
                    save(Path(m.name).name, tf.extractfile(m).read())  # type: ignore[union-attr]
        target = "aarch64-unknown-linux-gnu" if ARM else "x86_64-unknown-linux-gnu"
        save("deno", from_zip(fetch(_deno(target)), "deno"))
    else:
        sys.exit(f"Unsupported platform: {SYSTEM}")


def _deno(target: str) -> str:
    return f"https://github.com/denoland/deno/releases/download/v{DENO_VERSION}/deno-{target}.zip"


if __name__ == "__main__":
    main()
