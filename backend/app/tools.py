"""Locate, install and update the external tools: yt-dlp, ffmpeg, deno.

yt-dlp is used as a standalone build (not the Python package) so the app can
replace it without rebuilding itself. YouTube changes often, and an old yt-dlp
stops working within weeks, so the app checks for a new release on start.

We install the *onedir* zip builds (yt-dlp_macos.zip, yt-dlp_win.zip, ...)
rather than the single-file executables: a single-file build unpacks itself to
a fresh temp folder on every run, which macOS Gatekeeper and Windows Defender
rescan each time (~13 s per song on macOS). The onedir build is scanned once.
Onedir builds cannot `yt-dlp -U`, so updating is done here: compare the latest
GitHub release tag with the installed one and swap in the new folder.
"""

from __future__ import annotations

import asyncio
import logging
import os
import platform
import re
import shutil
import stat
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from . import config

log = logging.getLogger("sarki.tools")

RELEASES = "https://github.com/yt-dlp/yt-dlp/releases"
YTDLP_HOME = config.DATA_DIR / "ytdlp"
CURRENT_FILE = YTDLP_HOME / "current"


def _ytdlp_zip() -> str:
    arm = platform.machine().lower() in ("aarch64", "arm64")
    if config.SYSTEM == "Darwin":
        return "yt-dlp_macos.zip"  # universal2
    if config.SYSTEM == "Windows":
        return "yt-dlp_win_arm64.zip" if arm else "yt-dlp_win.zip"
    return "yt-dlp_linux_aarch64.zip" if arm else "yt-dlp_linux.zip"


def subprocess_env() -> dict[str, str]:
    """Environment for child processes: bundled bin dir first on PATH."""
    env = dict(os.environ)
    if config.BUNDLED_BIN_DIR and config.BUNDLED_BIN_DIR.is_dir():
        env["PATH"] = str(config.BUNDLED_BIN_DIR) + os.pathsep + env.get("PATH", "")
    # PyInstaller sets these for its own process; children must not inherit them.
    for key in ("LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH"):
        orig = env.pop(f"{key}_ORIG", None)
        if orig is not None:
            env[key] = orig
        elif config.FROZEN:
            env.pop(key, None)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def which(name: str) -> str | None:
    return shutil.which(name, path=subprocess_env()["PATH"])


@dataclass
class ToolState:
    ytdlp: str | None = None
    ytdlp_version: str | None = None
    ytdlp_managed: bool = False  # True when we own the install and may update it
    ffmpeg: str | None = None
    deno: str | None = None
    updating: bool = False
    update_message: str | None = None
    error: str | None = None
    ready: asyncio.Event = field(default_factory=asyncio.Event)

    def public(self) -> dict:
        return {
            "ytdlp_version": self.ytdlp_version,
            "ytdlp_ok": self.ytdlp is not None,
            "ffmpeg_ok": self.ffmpeg is not None,
            "deno_ok": self.deno is not None,
            "updating": self.updating,
            "update_message": self.update_message,
            "error": self.error,
            "ready": self.ready.is_set(),
        }


state = ToolState()


# ---- managed yt-dlp install ---------------------------------------------------
def _executable_in(folder: Path) -> Path | None:
    for p in folder.iterdir():
        if p.is_file() and p.name.startswith("yt-dlp"):
            return p
    return None


def _installed() -> tuple[str, Path] | None:
    try:
        tag = CURRENT_FILE.read_text().strip()
    except OSError:
        return None
    exe = _executable_in(YTDLP_HOME / tag) if (YTDLP_HOME / tag).is_dir() else None
    return (tag, exe) if exe else None


def _latest_tag() -> str:
    """Resolve /releases/latest via its redirect; no API token or rate limit."""
    req = urllib.request.Request(f"{RELEASES}/latest", method="HEAD", headers={"User-Agent": "sarki-indirici"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        final = resp.geturl()
    m = re.search(r"/tag/([^/?#]+)", final)
    if not m:
        raise RuntimeError(f"unexpected release URL {final}")
    return m.group(1)


def _install(tag: str) -> Path:
    url = f"{RELEASES}/download/{tag}/{_ytdlp_zip()}"
    log.info("Installing yt-dlp %s from %s", tag, url)
    YTDLP_HOME.mkdir(parents=True, exist_ok=True)
    zpath = YTDLP_HOME / f"{tag}.zip.part"
    staging = YTDLP_HOME / f".{tag}.staging"
    shutil.rmtree(staging, ignore_errors=True)
    req = urllib.request.Request(url, headers={"User-Agent": "sarki-indirici"})
    with urllib.request.urlopen(req, timeout=300) as resp, open(zpath, "wb") as fh:
        shutil.copyfileobj(resp, fh)
    with zipfile.ZipFile(zpath) as zf:
        for info in zf.infolist():
            target = staging / info.filename
            if not target.resolve().is_relative_to(staging.resolve()):
                raise RuntimeError("unsafe path in yt-dlp archive")
            zf.extract(info, staging)
            mode = (info.external_attr >> 16) & 0o777
            if mode and not info.is_dir():
                os.chmod(target, mode)
    zpath.unlink(missing_ok=True)
    exe = _executable_in(staging)
    if not exe:
        raise RuntimeError("yt-dlp executable not found in archive")
    exe.chmod(exe.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    final = YTDLP_HOME / tag
    shutil.rmtree(final, ignore_errors=True)
    staging.rename(final)
    CURRENT_FILE.write_text(tag)
    return _executable_in(final)  # type: ignore[return-value]


def _cleanup(keep: str) -> None:
    for p in YTDLP_HOME.iterdir():
        if p.is_dir() and p.name != keep:
            shutil.rmtree(p, ignore_errors=True)
        elif p.name.endswith(".part"):
            p.unlink(missing_ok=True)


def _ensure_latest(allow_update: bool) -> tuple[str, Path, bool]:
    """Return (tag, exe, updated). Installs when missing, updates when allowed."""
    current = _installed()
    if current and not allow_update:
        return current[0], current[1], False
    try:
        latest = _latest_tag()
    except Exception as exc:
        if current:
            log.info("Update check failed (%s); keeping yt-dlp %s", exc, current[0])
            return current[0], current[1], False
        raise
    if current and current[0] == latest:
        return current[0], current[1], False
    exe = _install(latest)
    _cleanup(keep=latest)
    return latest, exe, current is not None


# ---- process helpers ------------------------------------------------------------
async def _run(*args: str, timeout: float = 120) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=subprocess_env(),
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout)
    except TimeoutError:
        proc.kill()
        return -1, "timeout"
    return proc.returncode or 0, out.decode("utf-8", "replace")


async def _version(binary: str) -> str | None:
    # The first run of a fresh install also pays the one-time OS malware scan.
    code, out = await _run(binary, "--version", timeout=120)
    return out.strip().splitlines()[-1] if code == 0 and out.strip() else None


async def setup() -> None:
    """Resolve every tool; install or update yt-dlp as needed."""
    try:
        state.ffmpeg = which("ffmpeg")
        state.deno = which("deno")

        override = os.environ.get("YTDLP_PATH")
        if override:
            state.ytdlp = override
        else:
            state.updating = True
            try:
                tag, exe, updated = await asyncio.to_thread(_ensure_latest, config.AUTO_UPDATE)
                state.ytdlp, state.ytdlp_managed = str(exe), True
                if updated:
                    state.update_message = f"İndirme motoru güncellendi ({tag})."
            except Exception as exc:  # offline on first launch, GitHub down...
                log.warning("yt-dlp install failed: %s", exc)
                state.ytdlp = which("yt-dlp")
            finally:
                state.updating = False

        if state.ytdlp is None:
            state.error = (
                "İndirme motoru kurulamadı. İnternet bağlantını kontrol edip "
                "uygulamayı yeniden başlat."
            )
            return

        state.ytdlp_version = await _version(state.ytdlp)

        if state.ffmpeg is None:
            state.error = "ffmpeg bulunamadı; MP3 dönüştürme yapılamaz."
    finally:
        state.updating = False
        state.ready.set()


async def update_now(busy: bool = False) -> dict:
    if not state.ytdlp_managed:
        return {"updated": False, "message": "Bu kurulumda motor güncellemesi elle yapılıyor."}
    if busy:
        return {"updated": False, "message": "İndirmeler bitince tekrar dene."}
    state.updating = True
    try:
        tag, exe, updated = await asyncio.to_thread(_ensure_latest, True)
        state.ytdlp = str(exe)
        state.ytdlp_version = await _version(state.ytdlp)
    except Exception as exc:
        log.warning("manual update failed: %s", exc)
        return {"updated": False, "message": "Güncelleme başarısız oldu. İnternet bağlantını kontrol et."}
    finally:
        state.updating = False
    if updated:
        return {"updated": True, "message": f"Güncellendi: {state.ytdlp_version}"}
    return {"updated": False, "message": "Zaten en güncel sürüm."}
