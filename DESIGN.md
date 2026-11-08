---
name: Bedava ve Reklamsız MP3 Şarkı İndirici
description: Local YouTube to MP3 downloader, styled as Turkish highway signage
colors:
  motorway-green: "#0b6b3a"
  motorway-green-light: "#0e7d45"
  intercity-blue: "#0a4f8f"
  intercity-blue-light: "#0d5fa8"
  sign-yellow: "#f2b705"
  sign-yellow-light: "#ffc82e"
  signal-red: "#e0303f"
  signal-red-ink: "#ffb3ba"
  reflective-white: "#ffffff"
  night-asphalt: "#0f1612"
  asphalt-raised: "#16211b"
  asphalt-high: "#1f2d25"
  lane-line: "#2b3b32"
  ink: "#f2f5f3"
  ink-muted: "#b4c6bb"
  ink-faint: "#8aa093"
typography:
  display:
    fontFamily: "Overpass, ui-sans-serif, system-ui, sans-serif"
    fontSize: "2.75rem"
    fontWeight: 900
    lineHeight: 1
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "Overpass, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 900
    lineHeight: 1.25
  title:
    fontFamily: "Overpass, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 800
    lineHeight: 1.4
  body:
    fontFamily: "Overpass, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Overpass, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 800
    lineHeight: 1.2
rounded:
  sm: "8px"
  md: "12px"
  lg: "16px"
  sign: "18px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "40px"
components:
  button-primary:
    backgroundColor: "{colors.sign-yellow}"
    textColor: "{colors.night-asphalt}"
    typography: "{typography.title}"
    rounded: "{rounded.md}"
    padding: "0 32px"
    height: "64px"
  button-primary-hover:
    backgroundColor: "{colors.sign-yellow-light}"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "0 16px"
    height: "44px"
  input-search:
    backgroundColor: "{colors.reflective-white}"
    textColor: "{colors.night-asphalt}"
    rounded: "{rounded.md}"
    height: "64px"
  select-quality:
    backgroundColor: "{colors.motorway-green}"
    textColor: "{colors.reflective-white}"
    rounded: "{rounded.md}"
    height: "64px"
  sign-motorway:
    backgroundColor: "{colors.motorway-green}"
    textColor: "{colors.reflective-white}"
    rounded: "{rounded.sign}"
  sign-intercity:
    backgroundColor: "{colors.intercity-blue}"
    textColor: "{colors.reflective-white}"
    rounded: "{rounded.sign}"
  queue-row:
    backgroundColor: "{colors.asphalt-raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
---

# Design System: Bedava ve Reklamsız MP3 Şarkı İndirici

## Overview

**Creative North Star: "Yol Levhası" (The Road Sign)**

The songs are going into the car, so the interface speaks the language of Turkish highway signage. The one thing you must read first, the link field, sits on a fully saturated motorway-green sign with a white reflective border. Everything else is night asphalt: quiet, dark, and easy to scan. Signage is the only world the app borrows, and it supplies four things: type, palette, density and one signature move. Layout and controls stay ordinary web controls that any non-technical user already knows.

The signature move is the lit destination sign. While a song downloads, its row turns into a blue intercity sign panel with the same reflective border. Finished and waiting rows go back to dim asphalt. That way the screen always shows which song is "on the road" right now.

**Key Characteristics:**
- One saturated sign field per job: green for input, blue for the active download.
- A white reflective border inset from the field's edge, never a thin outline.
- Overpass, from the Highway Gothic lineage, in heavy weights; tabular figures for every number.
- Generous 64px controls for older, non-technical users.
- Plain Turkish copy, never technical jargon.

## Colors

A night-road palette: saturated sign fields on a dark green-black asphalt ground, with yellow reserved for the one thing to press.

### Primary
- **Motorway Green** (motorway-green): the header sign field. It fills the whole panel; it is not used as an accent.
- **Intercity Blue** (intercity-blue): the field of the active download row only.

### Secondary
- **Sign Yellow** (sign-yellow): the primary action (Ara/Getir, İndir, Hepsini indir), the progress fill, the focus ring and the text selection.

### Tertiary
- **Signal Red** (signal-red): the error mark. Its light tint (signal-red-ink) carries error text on dark ground.

### Neutral
- **Night Asphalt** (night-asphalt): the page ground.
- **Raised Asphalt** (asphalt-raised): queue rows, result lists and preview strips.
- **High Asphalt** (asphalt-high): image placeholders, step badges and ghost hovers.
- **Lane Line** (lane-line): dividers, dashed empty-state border and the scrollbar thumb.
- **Ink / Ink Muted / Ink Faint**: primary, secondary and tertiary text, all tinted green rather than plain grey.

### Named Rules
**The Field Not Accent Rule.** Green and blue appear only as whole sign fields with the reflective border, never as a stray text colour or a thin stripe.

**The One Lit Sign Rule.** Only active downloads use Intercity Blue. When nothing is downloading, the only sign on screen is the green header.

## Typography

**Display Font:** Overpass (self-hosted through @fontsource, with ui-sans-serif as fallback)
**Body Font:** Overpass

**Character:** A single highway grotesk at several weights. Hierarchy comes from scale and weight, never from a second typeface.

### Hierarchy
- **Display** (900, 2.75rem desktop / 2rem mobile, 1): product name on the header sign.
- **Headline** (900, 1.5rem): section headings such as "İndirmeler".
- **Title** (800, 1.0625–1.25rem): song titles and button labels.
- **Body** (400, 1.0625rem, 1.5): hints and helper text.
- **Label** (800, 0.9375rem): small action buttons and the "Bedava ve Reklamsız" plate.

### Named Rules
**The Step Scale Rule.** Sizes come only from the fixed scale (0.8125 / 0.9375 / 1.0625 / 1.25 / 1.5 / 2 / 2.75rem). Never introduce an in-between size.

**The Tabular Rule.** Percentages, times and counts always use tabular figures.

## Layout

A single centred column, at most 1080px wide, with a 16px gutter on phones and 32px on desktop. Reading order: header sign, then notices, then results, then the download queue, then the footer. Inside the header sign, the field, quality select and button sit in one row on desktop and stack full-width below 640px. Queue rows use a fixed grid with columns for the status mark, cover, text and actions, so the state mark is always in the same place. On phones, action buttons collapse to icons with screen-reader labels, and the percentage moves into the status line.

## Elevation & Depth

The page is mostly flat and uses tonal layering on asphalt. Only sign panels lift, using a soft shadow that falls downward.

### Shadow Vocabulary
- **Sign lift** (`box-shadow: 0 0 0 4px <field>, 0 22px 40px -24px rgb(0 0 0 / 0.75)`): every sign panel. The first layer draws the field colour outside the white border, so the border reads as inset like a real reflective sign.

## Shapes

Signs have generously rounded corners (18px) with a 4px white border. Controls use 12px corners, rows 16px, and small buttons 8px. Status marks are circles: hollow means waiting, a pulsing yellow dot means active, filled white means done, red with an × means error, and dashed means canceled.

## Components

### Buttons
- **Primary:** sign yellow on asphalt-coloured text, 900 weight, 64px tall on the header sign, 56px for the preview "İndir" and 48px for "Hepsini indir". Hover brightens to sign-yellow-light, and pressing nudges the button down 1px.
- **Outline:** 2px ink-faint border with ink text, 44px tall; on hover the border and text turn yellow. Used for per-result "İndir".
- **Ghost:** no fill; on hover it gets asphalt-high. Used for row actions (Göster, İptal, Tekrar dene, ×).

### Inputs / Fields
- **Search field:** white field with asphalt text, 64px tall, a green icon on the left, and a placeholder tinted toward asphalt.
- **Quality select:** a motorway-green field with a 3px white border and a custom chevron.
- **Focus:** a 3px sign-yellow outline with a 3px offset, used everywhere.

### Queue Row (signature)
The resting row is raised asphalt with a transparent 4px border. While downloading or converting, the same row becomes an intercity sign with an inset white border, a yellow progress bar and a large tabular percentage. The change is a 500ms exponential ease-out.

### Header Sign
A motorway sign holds the product name, a white "Bedava ve Reklamsız" plate beside the name (never above it), a folder link, and the input row.

## Do's and Don'ts

### Do:
- **Do** give a new primary surface its own sign field with the reflective border.
- **Do** keep every control at least 44px tall, and main actions at 56–64px.
- **Do** write errors in plain Turkish that name the problem and what to do next.
- **Do** use Lucide icons at a 2px stroke.

### Don't:
- **Don't** put a small label or kicker above a heading. Supplementary plates sit beside the heading.
- **Don't** use green or blue as text colour or as thin side stripes.
- **Don't** light more than the active rows in intercity blue.
- **Don't** use emoji or Unicode glyphs as icons.
