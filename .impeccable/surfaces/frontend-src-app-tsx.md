---
version: 1
slug: "frontend-src-app-tsx"
primary_target: "frontend/src/App.tsx"
related_targets: ["frontend/src/index.css"]
---

# Ana ekran (indirici)

Scope: the single app screen (paste/search → preview → queue). Visitor mode: Operate.
Audience: non-technical Turkish users filling a USB stick for the car. Task: paste a YouTube link or search, pick quality, download, find the file.
Constraints: Turkish copy only, no jargon, large hit targets, keyboard usable, works offline-first (fonts self-hosted).

## Direction contract

THESIS: Songs bound for the car, spoken in Turkish highway-sign language: the input is the green motorway sign you read first, every download is a destination with its remaining distance. Refuses the category default of a white page, centred input and grey cards.

OWN-WORLD: Night asphalt ground (#0f1612) with a fully saturated motorway-green sign panel (#0b6b3a) carrying a white reflective border and rounded corners; the active row becomes a blue intercity sign panel (#0a4f8f) with the same border. Sign-yellow (#f2b705) for the one primary action, signal red (#c8102e) for errors. Overpass (Highway Gothic lineage) for everything, tabular figures for percentages and times. Lucide icons, 2px stroke.

STORY: The visitor sees one big sign with one big field, pastes a link, sees the song with its cover, presses İndir, watches the row light up as it travels, then opens the folder. Errors explain what happened in plain Turkish and offer Tekrar dene.

FIRST VIEWPORT: Top: full-width green sign panel (white border) with the product name left, the destination folder as a small white plate right, and the large link/search field plus quality select and yellow button inside the sign. Below: preview strip (cover, title, artist, duration, İndir) or search results. Below that: the queue, each row a status mark in a fixed cell, title/artist, progress bar, big tabular readout on the right.

FORM: candidate 4 of 7 (Karayolları yön levhaları), seed:78e7222ff85820cd. Raises: fixed-cell state mark (timetable), active row burns brightest (transit), colour as a field not an accent (acetate), hierarchy by scale contrast (specimen), strict step type scale (bitmap).

Signature move: the active download row is a lit blue destination sign with a reflective border; others stay dim asphalt and readable.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
