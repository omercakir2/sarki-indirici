# syntax=docker/dockerfile:1.7

# ---- 1) Build the React UI --------------------------------------------------
FROM node:22-alpine AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- 2) deno (JS runtime yt-dlp needs for YouTube) --------------------------
FROM denoland/deno:bin-2.9.4 AS deno

# ---- 3) Runtime ---------------------------------------------------------------
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY --from=deno /deno /usr/local/bin/deno

WORKDIR /app
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir "fastapi>=0.115" "uvicorn>=0.32"
COPY backend/app ./app
COPY --from=web /web/dist ./web

ENV SARKI_IN_DOCKER=1 \
    SARKI_WEB_DIR=/app/web \
    SARKI_DATA_DIR=/data \
    SARKI_DOWNLOAD_DIR=/downloads \
    PYTHONUNBUFFERED=1

# yt-dlp itself is installed into /data on first start and kept up to date there.
VOLUME ["/data", "/downloads"]
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/api/status', timeout=4)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
