# Vinyl Queue — Project Overview

## What This Is

A local-network web app for dinner parties and home listening sessions. Guests connect via Wi-Fi, browse the host's record collection (synced from Discogs), and request albums to be played. Requests appear in a shared queue visible to everyone. Guests can up- or down-vote requests; the host has a PIN-activated control layer to manage the queue and trigger Discogs sync.

No user accounts. No login. Identity is tracked by IP address only.

---

## Core Features

### Guest Experience

- Browse the full record collection (search, filter by genre/artist/decade)
- View album details (cover art, tracklist, label, year — pulled from Discogs)
- Request an album to be added to the queue
- Cancel their own pending request
- Thumb up or thumb down any queued album (one vote per IP per album)
- See the live queue update in real time (WebSocket or SSE)

### Queue Behaviour

- First-come-first-served ordering — votes do not reorder the queue
- Down-vote count is surfaced prominently to the host as a "skip signal"
- Each album can only appear in the queue once at a time
- Guests can only have one active request at a time

### Host Mode

- Activated by entering a PIN on the same page as guests (no separate URL)
- PIN is simple and set in server config — no strong security required
- Once activated, host controls appear inline on the queue
- Host controls:
  - Mark the current (or any) album as **Played** (removes from queue)
  - **Skip / Remove** any album from the queue
  - See down-vote counts clearly highlighted as skip signals
  - **Trigger Discogs sync** (re-imports the collection from the API)
  - Deactivate host mode

### Discogs Integration

- Collection data is fetched from the Discogs API using a user-provided token
- Sync is manual and on-demand, triggered from host mode only
- Sync fetches the authenticated user's Discogs collection and upserts records into the local database
- Data stored locally: artist, title, year, label, genre/style tags, cover art URL, Discogs release ID
- Tracklist is displayed in the UI but is not stored locally — it is fetched from the Discogs API at display time only
- Cover art is referenced by URL (not downloaded/cached locally, unless implementation finds this necessary for performance)

---

## Identity & Multi-User Behaviour

- No accounts, no cookies required for identity
- Each visitor is identified by their IP address
- IP is used to: attribute queue requests, attribute votes, enforce one-request and one-vote-per-album limits
- Guest-facing UI should feel anonymous — no "logged in as" language

---

## Real-Time Updates

- The queue and vote counts should update live for all connected guests without requiring a page refresh
- Use Server-Sent Events (SSE)

---

## Design & UI

- Visual design will be provided as a completed Stitch (Google) design — Claude should implement it faithfully
- The app is a single page (or feels like one) — no multi-page navigation
- Mobile-first: guests will primarily use phones

---

## Tech Stack

- Stack, framework, and database decisions are defined in the project's existing `CLAUDE.md` and standards docs, which will be present in the project folder before coding begins
- Claude Code should read those docs first and follow their conventions
- Prefer SQLite for local simplicity unless the standards docs specify otherwise

---

## Out of Scope (for now)

- Actual music playback or Spotify/streaming integration
- Push notifications
- Persistent history across sessions (queue clears on server restart is acceptable)
- Admin user management
- Public internet access / deployment
