---
date: 2026-03-25
topic: vinyl-queue-app
---

# Vinyl Queue — Application Requirements

## Problem Frame

Dinner party hosts with vinyl collections have no easy way to let guests browse and request albums. The alternative is shouting across the room or hovering over the host's shoulder. Vinyl Queue gives guests agency over the listening experience while keeping the host in control of the turntable.

## Requirements

### Navigation & Layout

- R1. Single-page mobile-first app with a two-tab bottom navigation bar: "The Crate" (collection browse) and "Queue"
- R2. Guests land on The Crate view by default
- R3. Host mode controls appear inline on the Queue view when activated — no separate host URL or page

### The Crate (Collection Browse)

- R4. Text search input at the top of The Crate view for searching by artist or album title
- R5. Genre and decade chip filters below the search input; chips are populated from the synced collection data
- R6. Albums displayed in a 2-column grid of album cards showing cover art, title, artist, and year
- R7. Tapping an album card opens an album detail overlay (not a new page) showing: large cover art, label, title, artist, year, genre/style chips, description (if available), tracklist, and a "Request This Album" button
- R8. The "Request This Album" button is disabled with appropriate feedback if the album is already in the queue or the guest has reached their request limit

### Queue

- R9. The queue view has a "Now Playing" slot at the top showing the album cover art, title, artist, and album name
- R10. Below Now Playing, an "Up Next" section lists queued albums in first-come-first-served order with a count of albums in the queue
- R11. Votes do not reorder the queue — ordering is strictly insertion order
- R12. Each album can only appear in the queue once at a time
- R13. All connected clients see queue and vote updates in real time via Server-Sent Events (SSE)

### Guest Interactions

- R14. Guests are identified by IP address — no accounts, no login, no cookies required for identity
- R15. Guests can request albums to be added to the queue, up to 3 active requests at a time; once a request is played or removed, they can request again
- R16. Guests can cancel their own pending requests
- R17. Guests can thumb-up or thumb-down any queued album (one vote per guest per album)
- R18. Votes are changeable — a guest can switch between up-vote, down-vote, or remove their vote
- R19. Guest-facing UI feels anonymous — no "logged in as" language

### Host Mode

- R20. Activated by tapping a lock icon in the header, which opens a 4-digit numeric PIN keypad overlay
- R21. PIN is set in server configuration — no strong security required
- R22. No "Forgot PIN" functionality — PIN is shared verbally
- R23. Once activated, a "HOST MODE ACTIVE" indicator is visible and host controls appear inline on the queue view
- R24. Host can promote any queued album to "Now Playing" — this removes it from the queue and places it in the Now Playing slot
- R25. Host can skip/remove any album from the queue
- R26. Host sees down-vote counts prominently highlighted as skip signals
- R27. Host can trigger a Discogs collection sync from the queue view
- R28. Host can deactivate host mode

### Discogs Integration

- R29. Collection is fetched from the Discogs API using a user-provided token configured on the server
- R30. Sync is manual and on-demand, triggered by the host only
- R31. Sync upserts records into the local database: artist, title, year, label, genre/style tags, cover art URL, Discogs release ID
- R32. Tracklists are fetched from the Discogs API on first view of an album detail, then cached locally for subsequent views
- R33. Cover art is referenced by Discogs URL (not downloaded locally)
- R34. When sync completes, connected clients receive a silent background refresh via SSE — The Crate updates without interruption

### Real-Time Updates

- R35. Queue state (additions, removals, Now Playing changes) broadcasts to all clients via SSE
- R36. Vote count changes broadcast to all clients via SSE
- R37. Collection sync completion broadcasts to all clients via SSE

## Success Criteria

- Guests on the same Wi-Fi network can browse, search, and request albums within seconds of connecting
- The queue updates live for all connected clients without page refresh
- The host can manage the full queue lifecycle (promote, skip, remove) from their phone
- A Discogs collection of 500+ albums syncs and is browsable with acceptable performance

## Scope Boundaries

- No music playback or streaming integration
- No push notifications
- No persistent history across server restarts (queue clears on restart)
- No admin user management
- No public internet deployment — local network only
- No account creation or authentication beyond the host PIN
- No album descriptions stored locally — only displayed if available from Discogs

## Key Decisions

- **Now Playing is an explicit state**: Host promotes a queue item to Now Playing via a button. It is not implicit from queue position.
- **3 requests per guest**: Balances fairness with allowing guests to shape the evening. More generous than one-at-a-time.
- **Votes are changeable**: Guests can switch or remove votes freely. Keeps it low-stakes and social.
- **Tracklists cached after first fetch**: Reduces Discogs API calls during a party while keeping the initial sync lightweight.
- **Silent sync refresh**: Discogs sync doesn't interrupt guests browsing the collection.
- **No Forgot PIN**: The PIN is trivial and shared verbally — recovery UX is unnecessary.
- **Album cover art in Now Playing**: Shows the actual album cover, not a stylized turntable.

## Dependencies / Assumptions

- Host has a Discogs account with a collection and an API token
- All guests are on the same local network as the server
- Discogs API rate limits are sufficient for a party-sized group browsing album details

## Outstanding Questions

### Deferred to Planning

- [Affects R32][Needs research] What are the Discogs API rate limits, and do we need request queuing or throttling for tracklist fetches?
- [Affects R6][Technical] How should the collection grid handle very large collections (1000+ albums) — virtual scrolling, pagination, or lazy loading?
- [Affects R34][Technical] What SSE event structure best supports the different update types (queue, votes, collection sync)?
- [Affects R9][Technical] What happens to Now Playing when the server restarts — does it clear along with the queue?
- [Affects R5][Technical] Should genre/decade chip filters be multi-select (e.g., Jazz AND Soul) or single-select?

## Design Reference

Wireframes and design system documentation are in `docs/wireframes/`:
- `main_page_queue/` — The Crate browse view
- `album_detail_overlay/` — Album detail overlay
- `host_mode_active/` — Host mode with Now Playing and queue
- `pin_entry_overlay/` — PIN entry keypad
- `electric_record_shop/DESIGN.md` — "Digital Neon Tactility" design system

## Next Steps

→ `/ce:plan` for structured implementation planning
