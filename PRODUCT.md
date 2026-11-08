# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Vite + React + Tailwind CSS frontend, served as static files by a Python FastAPI backend. Runs locally only: as a Docker container, or packaged as a double-clickable desktop app (pywebview + PyInstaller). Download engine: yt-dlp binary + ffmpeg + deno.

## Users

The owner and their non-technical friends. They find a song on YouTube, want it as an MP3 file, and usually copy it to a USB stick (flash drive) for the car or another player. They are not developers, do not know what a terminal is, and today they use ad-filled converter sites.

## Product Purpose

Paste a YouTube link (or search for a song), get a clean, properly tagged MP3 in the Downloads folder. No ads, no pop-ups, no fake "Download" buttons, no account. Success: a friend opens the app, downloads a song, and finds it in their Downloads folder without asking for help.

## Positioning

Free and ad-free, running on the user's own computer. Unlike online converter sites it has no ads, redirects or tracking, and files carry the cover art and artist/title tags.

## Operating Context

- Launched by double-click (desktop app window) or at localhost in a browser (Docker).
- Typical flow: copy link from YouTube → paste → pick quality → download → open folder → copy to USB.
- Sometimes a whole playlist at once.
- Files land in `~/Downloads/Sarki-Indirici/` (or the Docker volume).

## Capabilities and Constraints

- YouTube only (single videos, playlists, search). Spotify is out of scope.
- MP3 output at 128 / 192 / 320 kbps with embedded cover art and ID3 tags.
- Live progress, a queue of multiple downloads, "open folder" action.
- Local use only; no accounts, no server hosting, no analytics.
- yt-dlp breaks when YouTube changes; the app self-updates the yt-dlp binary on start.
- Unsigned app: first launch shows an OS warning (SmartScreen / Gatekeeper).

## Brand Commitments

- Name: **Bedava ve Reklamsız MP3 Şarkı İndirici** (user-chosen).
- UI language: Turkish only.
- Voice: plain, friendly Turkish a non-technical person understands; no jargon (no "yt-dlp", "bitrate" without explanation).

## Evidence on Hand

None. No logos, testimonials or usage numbers exist; do not invent them.

## Product Principles

1. One obvious action: paste a link, get a file.
2. Never look like an ad-ridden converter site; trust comes from calm, honest UI.
3. Errors are explained in plain Turkish with what to do next.
4. Works for someone who has never used a terminal.

## Accessibility & Inclusion

Keyboard usable, readable contrast, large hit targets; users may be older relatives.
