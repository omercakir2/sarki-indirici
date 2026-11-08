"""FastAPI app: JSON API under /api, built frontend everywhere else."""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config, tools, ytdlp
from .jobs import manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("sarki")


@asynccontextmanager
async def lifespan(app: FastAPI):
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    setup_task = asyncio.create_task(tools.setup())
    manager.start()
    yield
    setup_task.cancel()
    await manager.stop()


app = FastAPI(title=config.APP_NAME, lifespan=lifespan)


# ---- models ------------------------------------------------------------------
class LookupIn(BaseModel):
    url: str = Field(min_length=1, max_length=2000)


class TrackIn(BaseModel):
    url: str
    title: str | None = None
    artist: str | None = None
    thumbnail: str | None = None
    duration: float | None = None


class JobsIn(BaseModel):
    tracks: list[TrackIn] = Field(min_length=1, max_length=500)
    quality: str = "192"


# ---- API ---------------------------------------------------------------------
@app.get("/api/status")
async def status():
    return {
        "app": config.APP_NAME,
        "download_dir": str(config.DOWNLOAD_DIR),
        "can_open_folder": config.CAN_OPEN_FOLDER,
        "desktop": config.FROZEN,
        **tools.state.public(),
    }


@app.post("/api/lookup")
async def lookup(body: LookupIn):
    try:
        return await ytdlp.lookup(body.url)
    except ytdlp.UserError as exc:
        raise HTTPException(422, str(exc)) from None


@app.get("/api/search")
async def search(q: str):
    if len(q) > 200:
        raise HTTPException(422, "Arama çok uzun.")
    try:
        return {"results": await ytdlp.search(q)}
    except ytdlp.UserError as exc:
        raise HTTPException(422, str(exc)) from None


@app.get("/api/jobs")
async def list_jobs():
    return {"jobs": manager.list()}


@app.post("/api/jobs")
async def add_jobs(body: JobsIn):
    for t in body.tracks:
        if not ytdlp.is_youtube_url(t.url):
            raise HTTPException(422, "Şimdilik sadece YouTube bağlantıları destekleniyor.")
    jobs = [manager.add(t.model_dump(), body.quality) for t in body.tracks]
    return {"jobs": [j.public() for j in jobs]}


@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    if not manager.cancel(job_id):
        raise HTTPException(404, "İndirme bulunamadı.")
    return {"ok": True}


@app.post("/api/jobs/{job_id}/retry")
async def retry_job(job_id: str):
    job = manager.retry(job_id)
    if not job:
        raise HTTPException(404, "İndirme bulunamadı.")
    return job.public()


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    if not manager.remove(job_id):
        raise HTTPException(404, "İndirme bulunamadı.")
    return {"ok": True}


@app.post("/api/jobs/clear")
async def clear_jobs():
    return {"removed": manager.clear_finished()}


@app.get("/api/jobs/{job_id}/file")
async def job_file(job_id: str):
    """Send the finished MP3 to the browser (useful when running in Docker)."""
    job = manager.jobs.get(job_id)
    if not job or job.status != "done" or not job.filepath:
        raise HTTPException(404, "Dosya hazır değil.")
    path = Path(job.filepath).resolve()
    if config.DOWNLOAD_DIR.resolve() not in path.parents or not path.is_file():
        raise HTTPException(404, "Dosya bulunamadı; taşınmış ya da silinmiş olabilir.")
    return FileResponse(path, media_type="audio/mpeg", filename=path.name)


@app.get("/api/events")
async def events():
    async def stream():
        q = manager.subscribe()
        try:
            yield f"data: {json.dumps({'type': 'snapshot', 'jobs': manager.list()})}\n\n"
            while True:
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=15)
                    yield f"data: {json.dumps(msg)}\n\n"
                except TimeoutError:
                    yield ": ping\n\n"
        finally:
            manager.unsubscribe(q)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/open-folder")
async def open_folder(job_id: str | None = None):
    if not config.CAN_OPEN_FOLDER:
        raise HTTPException(400, "Bu kurulumda klasör açılamıyor.")
    folder = config.DOWNLOAD_DIR
    folder.mkdir(parents=True, exist_ok=True)
    target = None
    if job_id and (job := manager.jobs.get(job_id)) and job.filepath and Path(job.filepath).exists():
        target = Path(job.filepath)
    if config.SYSTEM == "Darwin":
        cmd = ["open", "-R", str(target)] if target else ["open", str(folder)]
    elif config.SYSTEM == "Windows":
        cmd = ["explorer", f"/select,{target}"] if target else ["explorer", str(folder)]
    else:
        cmd = ["xdg-open", str(folder)]
    subprocess.Popen(cmd, env=tools.subprocess_env())
    return {"ok": True}


@app.post("/api/update")
async def update_engine():
    busy = any(j["status"] in ("downloading", "converting") for j in manager.list())
    return await tools.update_now(busy=busy)


# ---- frontend ----------------------------------------------------------------
if config.WEB_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=config.WEB_DIR / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    async def spa(path: str):
        if path.startswith("api/"):
            raise HTTPException(404)
        candidate = (config.WEB_DIR / path).resolve()
        if path and candidate.is_file() and config.WEB_DIR.resolve() in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(config.WEB_DIR / "index.html")
else:
    log.warning("Frontend build not found at %s; serving API only.", config.WEB_DIR)
