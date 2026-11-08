"""Thin async wrapper around the yt-dlp binary: lookup, search, download."""

from __future__ import annotations

import asyncio
import json
import re
from urllib.parse import parse_qs, urlparse

from . import config, tools

QUALITIES = {"128": "128K", "192": "192K", "320": "320K"}

YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "www.youtu.be",
}


class UserError(Exception):
    """An error whose message is safe and meaningful to show the user (Turkish)."""


def friendly_error(raw: str) -> str:
    text = raw.lower()
    if "sign in to confirm" in text or "not a bot" in text:
        return "YouTube bu bağlantıyı geçici olarak engelledi. Birkaç dakika sonra tekrar dene."
    if "private video" in text:
        return "Bu video gizli, indirilemiyor."
    if "members-only" in text or "join this channel" in text:
        return "Bu video sadece kanal üyelerine açık."
    if "age" in text and ("restricted" in text or "confirm your age" in text):
        return "Bu video yaş sınırlı, giriş yapmadan indirilemiyor."
    if "unavailable" in text or "not available" in text or "has been removed" in text:
        return "Bu video artık yok ya da senin bölgende açılmıyor."
    if "is not a valid url" in text or "unsupported url" in text:
        return "Bu bir YouTube bağlantısına benzemiyor."
    if "live event" in text or "is live" in text or "premieres in" in text:
        return "Canlı yayınlar ve henüz başlamamış videolar indirilemez."
    if (
        "unable to download" in text
        or "timed out" in text
        or "getaddrinfo" in text
        or "network is unreachable" in text
        or "connection" in text
    ):
        return "İnternete bağlanılamadı. Bağlantını kontrol edip tekrar dene."
    if "ffmpeg" in text or "ffprobe" in text:
        return "Ses dönüştürülürken sorun çıktı (ffmpeg)."
    return "Bir şeyler ters gitti. Bağlantıyı kontrol edip tekrar dene."


def is_youtube_url(text: str) -> bool:
    try:
        parsed = urlparse(text.strip())
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and (parsed.hostname or "") in YOUTUBE_HOSTS


def normalize_url(text: str) -> str:
    """Strip tracking params; keep v= and list=. A watch URL with list= stays a video."""
    url = text.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def _is_playlist_url(url: str) -> bool:
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    return parsed.path.rstrip("/") == "/playlist" and "list" in qs


def thumbnail_for(url: str) -> str | None:
    """Best-effort cover URL from a YouTube watch/short link."""
    parsed = urlparse(url)
    vid = parse_qs(parsed.query).get("v", [None])[0]
    if not vid and parsed.hostname in ("youtu.be", "www.youtu.be"):
        vid = parsed.path.strip("/") or None
    return f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg" if vid else None


def _thumb(entry: dict) -> str | None:
    if entry.get("thumbnail"):
        return entry["thumbnail"]
    thumbs = entry.get("thumbnails") or []
    if thumbs:
        # Pick a mid-size one: last is usually the largest.
        best = sorted(thumbs, key=lambda t: (t.get("width") or 0))
        mid = [t for t in best if (t.get("width") or 0) >= 300]
        return (mid[0] if mid else best[-1]).get("url")
    vid = entry.get("id")
    return f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg" if vid else None


def _track(entry: dict) -> dict:
    vid = entry.get("id")
    url = entry.get("webpage_url") or entry.get("url")
    if vid and (not url or not str(url).startswith("http")):
        url = f"https://www.youtube.com/watch?v={vid}"
    return {
        "id": vid,
        "url": url,
        "title": entry.get("track") or entry.get("title") or "Adsız",
        "artist": entry.get("artist") or entry.get("channel") or entry.get("uploader"),
        "duration": entry.get("duration"),
        "thumbnail": _thumb(entry),
    }


async def _json(*args: str, timeout: float = 60) -> dict:
    await tools.state.ready.wait()
    if not tools.state.ytdlp:
        raise UserError(tools.state.error or "İndirme motoru hazır değil.")
    proc = await asyncio.create_subprocess_exec(
        tools.state.ytdlp,
        "-J",
        "--no-warnings",
        "--cache-dir",
        str(config.DATA_DIR / "cache"),
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=tools.subprocess_env(),
        **tools.NO_WINDOW,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout)
    except TimeoutError:
        proc.kill()
        raise UserError("YouTube çok geç cevap verdi. Tekrar dene.") from None
    if proc.returncode != 0:
        raise UserError(friendly_error(err.decode("utf-8", "replace")))
    return json.loads(out)


async def lookup(url: str) -> dict:
    """Return {"kind": "video"|"playlist", "title", "tracks": [...]}."""
    url = normalize_url(url)
    if not is_youtube_url(url):
        raise UserError("Şimdilik sadece YouTube bağlantıları destekleniyor.")
    if _is_playlist_url(url):
        data = await _json("--flat-playlist", url, timeout=90)
        tracks = [_track(e) for e in data.get("entries") or [] if e and e.get("id")]
        tracks = [t for t in tracks if t["duration"] is None or t["duration"] > 0]
        if not tracks:
            raise UserError("Bu oynatma listesi boş ya da gizli.")
        return {
            "kind": "playlist",
            "title": data.get("title") or "Oynatma listesi",
            "uploader": data.get("uploader") or data.get("channel"),
            "tracks": tracks,
        }
    data = await _json("--no-playlist", url)
    if data.get("is_live"):
        raise UserError("Canlı yayınlar indirilemez.")
    track = _track(data)
    return {"kind": "video", "title": track["title"], "tracks": [track]}


async def search(query: str, limit: int = 12) -> list[dict]:
    query = query.strip()
    if not query:
        return []
    data = await _json("--flat-playlist", f"ytsearch{limit}:{query}", timeout=60)
    return [
        _track(e)
        for e in data.get("entries") or []
        if e and e.get("id") and (e.get("duration") or 0) > 0  # drop live streams
    ]


# ---- downloading -----------------------------------------------------------

# One machine-readable line per progress tick.
PROGRESS_TEMPLATE = (
    "download:@@P %(progress.downloaded_bytes)s|%(progress.total_bytes)s|"
    "%(progress.total_bytes_estimate)s|%(progress.speed)s|%(progress.eta)s"
)
PROGRESS_RE = re.compile(r"^@@P (\S+)\|(\S+)\|(\S+)\|(\S+)\|(\S+)$")
DONE_PREFIX = "@@F "

# Square-crop the YouTube thumbnail so car stereos and phones show a proper cover.
SQUARE_COVER = (
    "ThumbnailsConvertor+FFmpeg_o:-c:v mjpeg -qmin 1 -qscale:v 2 "
    "-vf crop=\"'if(gt(ih,iw),iw,ih)':'if(gt(iw,ih),ih,iw)'\""
)


def download_args(url: str, quality: str, out_dir: str) -> list[str]:
    q = QUALITIES.get(quality, "192K")
    args = [
        tools.state.ytdlp or "yt-dlp",
        url,
        "--no-playlist",
        "--newline",
        "--progress",
        "--no-warnings",
        "--quiet",
        "--cache-dir",
        str(config.DATA_DIR / "cache"),
        "--progress-template",
        PROGRESS_TEMPLATE,
        "--print",
        f"after_move:{DONE_PREFIX}%(filepath)s",
        "-f",
        "bestaudio/best",
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        q,
        "--embed-metadata",
        "--embed-thumbnail",
        "--convert-thumbnails",
        "jpg",
        "--ppa",
        SQUARE_COVER,
        "--windows-filenames",  # safe on FAT32 USB sticks
        "--trim-filenames",
        "120",
        "--no-mtime",
        "--no-part",
        "-P",
        out_dir,
        "-P",
        "temp:" + str(config.DATA_DIR / "tmp"),
        "-o",
        "%(title)s.%(ext)s",
    ]
    if tools.state.ffmpeg:
        args += ["--ffmpeg-location", tools.state.ffmpeg]
    return args


def parse_progress(line: str) -> dict | None:
    m = PROGRESS_RE.match(line.strip())
    if not m:
        return None

    def num(s: str) -> float | None:
        try:
            return float(s)
        except ValueError:
            return None

    done, total, estimate, speed, eta = (num(g) for g in m.groups())
    total = total or estimate
    percent = (done / total * 100) if (done is not None and total) else None
    return {"percent": percent, "speed": speed, "eta": eta}
