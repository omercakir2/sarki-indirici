"""In-memory download queue with live updates pushed to SSE subscribers."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import config, tools, ytdlp

log = logging.getLogger("sarki.jobs")

ACTIVE = ("queued", "downloading", "converting")


@dataclass
class Job:
    id: str
    url: str
    title: str
    artist: str | None
    thumbnail: str | None
    duration: float | None
    quality: str
    status: str = "queued"  # queued | downloading | converting | done | error | canceled
    percent: float = 0.0
    speed: float | None = None
    eta: float | None = None
    error: str | None = None
    filename: str | None = None
    created: float = field(default_factory=time.time)
    filepath: str | None = field(default=None, repr=False)

    def public(self) -> dict:
        data = asdict(self)
        data.pop("filepath")
        return data


class JobManager:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._procs: dict[str, asyncio.subprocess.Process] = {}
        self._subscribers: set[asyncio.Queue[dict]] = set()
        self._workers: list[asyncio.Task] = []

    # -- lifecycle -----------------------------------------------------------
    def start(self) -> None:
        for _ in range(max(1, config.MAX_PARALLEL)):
            self._workers.append(asyncio.create_task(self._worker()))

    async def stop(self) -> None:
        for proc in list(self._procs.values()):
            proc.kill()
        for w in self._workers:
            w.cancel()

    # -- pub/sub -------------------------------------------------------------
    def subscribe(self) -> asyncio.Queue[dict]:
        q: asyncio.Queue[dict] = asyncio.Queue(maxsize=500)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[dict]) -> None:
        self._subscribers.discard(q)

    def _emit(self, job: Job) -> None:
        msg = {"type": "job", "job": job.public()}
        for q in list(self._subscribers):
            try:
                q.put_nowait(msg)
            except asyncio.QueueFull:
                pass  # a stalled client; it will resync on reconnect

    # -- API -----------------------------------------------------------------
    def add(self, track: dict, quality: str) -> Job:
        job = Job(
            id=uuid.uuid4().hex[:12],
            url=track["url"],
            title=track.get("title") or "Adsız",
            artist=track.get("artist"),
            thumbnail=track.get("thumbnail") or ytdlp.thumbnail_for(track["url"]),
            duration=track.get("duration"),
            quality=quality if quality in ytdlp.QUALITIES else "192",
        )
        self.jobs[job.id] = job
        self._queue.put_nowait(job.id)
        self._emit(job)
        return job

    def list(self) -> list[dict]:
        return [j.public() for j in sorted(self.jobs.values(), key=lambda j: j.created)]

    def cancel(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if not job or job.status not in ACTIVE:
            return False
        job.status = "canceled"
        proc = self._procs.get(job_id)
        if proc and proc.returncode is None:
            proc.kill()
        self._emit(job)
        return True

    def retry(self, job_id: str) -> Job | None:
        job = self.jobs.get(job_id)
        if not job or job.status not in ("error", "canceled"):
            return None
        job.status, job.percent, job.error = "queued", 0.0, None
        job.speed = job.eta = None
        self._queue.put_nowait(job.id)
        self._emit(job)
        return job

    def remove(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if not job:
            return False
        if job.status in ACTIVE:
            self.cancel(job_id)
        del self.jobs[job_id]
        for q in list(self._subscribers):
            try:
                q.put_nowait({"type": "removed", "id": job_id})
            except asyncio.QueueFull:
                pass
        return True

    def clear_finished(self) -> int:
        ids = [j.id for j in self.jobs.values() if j.status not in ACTIVE]
        for i in ids:
            self.remove(i)
        return len(ids)

    # -- worker --------------------------------------------------------------
    async def _worker(self) -> None:
        while True:
            job_id = await self._queue.get()
            job = self.jobs.get(job_id)
            if not job or job.status != "queued":
                continue
            try:
                await self._run(job)
            except Exception as exc:  # never let one job kill the worker
                log.exception("job %s crashed", job_id)
                job.status, job.error = "error", ytdlp.friendly_error(str(exc))
                self._emit(job)

    async def _run(self, job: Job) -> None:
        await tools.state.ready.wait()
        if not tools.state.ytdlp:
            job.status, job.error = "error", tools.state.error or "İndirme motoru hazır değil."
            self._emit(job)
            return

        config.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        (config.DATA_DIR / "tmp").mkdir(parents=True, exist_ok=True)
        job.status = "downloading"
        self._emit(job)

        proc = await asyncio.create_subprocess_exec(
            *ytdlp.download_args(job.url, job.quality, str(config.DOWNLOAD_DIR)),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=tools.subprocess_env(),
            **tools.NO_WINDOW,
        )
        self._procs[job.id] = proc
        stderr_chunks: list[str] = []

        async def read_stderr() -> None:
            assert proc.stderr
            async for raw in proc.stderr:
                stderr_chunks.append(raw.decode("utf-8", "replace"))

        err_task = asyncio.create_task(read_stderr())
        last_emit = 0.0
        assert proc.stdout
        async for raw in proc.stdout:
            line = raw.decode("utf-8", "replace").rstrip("\r\n")
            if line.startswith(ytdlp.DONE_PREFIX):
                job.filepath = line[len(ytdlp.DONE_PREFIX) :].strip()
                job.filename = Path(job.filepath).name
                continue
            prog = ytdlp.parse_progress(line)
            if not prog or job.status == "canceled":
                continue
            if prog["percent"] is not None:
                job.percent = min(prog["percent"], 100.0)
            job.speed, job.eta = prog["speed"], prog["eta"]
            if job.percent >= 99.9:
                job.status = "converting"
            now = time.monotonic()
            if now - last_emit > 0.25 or job.status == "converting":
                last_emit = now
                self._emit(job)

        await proc.wait()
        await err_task
        self._procs.pop(job.id, None)

        if job.status == "canceled":
            return
        if proc.returncode == 0 and job.filepath:
            job.status, job.percent, job.speed, job.eta = "done", 100.0, None, None
        else:
            stderr = "".join(stderr_chunks)
            log.warning("job %s failed (%s): %s", job.id, proc.returncode, stderr[-800:])
            job.status, job.error = "error", ytdlp.friendly_error(stderr)
        self._emit(job)


manager = JobManager()
