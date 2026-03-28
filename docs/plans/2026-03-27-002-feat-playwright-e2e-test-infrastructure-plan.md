---
title: "feat: Playwright E2E test infrastructure and full user journey tests"
type: feat
status: active
date: 2026-03-27
origin: docs/brainstorms/2026-03-27-playwright-e2e-tests-requirements.md
---

# feat: Playwright E2E test infrastructure and full user journey tests

E2E tests exercising full user journeys through the real UI + API, with database isolation via a temp SQLite file and a test-only reset endpoint.

(see origin: `docs/brainstorms/2026-03-27-playwright-e2e-tests-requirements.md`)

## Phase 1: Test Infrastructure

### 1a. Test reset router (backend)

**Create:** `apps/backend/src/cue_the_music/routers/test_router.py`

A `POST /api/test/reset` endpoint that:
1. Truncates `votes`, `queue_items`, `now_playing`, `albums` tables (in FK order)
2. Seeds baseline album data (see seed data below)
3. Returns 200 with `{"status": "reset"}`

**Modify:** `apps/backend/src/cue_the_music/main.py`

Conditionally mount the test router only when `TEST_MODE=true`:

```python
import os
if os.environ.get("TEST_MODE") == "true":
    from cue_the_music.routers.test_router import router as test_router
    app.include_router(test_router)
```

### 1b. Seed data

6 albums covering diverse genres, decades, and tracklist states:

| Artist | Title | Year | Genres | Styles | Tracklist |
|--------|-------|------|--------|--------|-----------|
| Miles Davis | Kind of Blue | 1959 | Jazz | Modal | Yes (2 tracks) |
| The Clash | London Calling | 1979 | Rock | Punk | Yes (2 tracks) |
| Kraftwerk | Trans-Europe Express | 1977 | Electronic | Synth-pop | Yes (2 tracks) |
| Metallica | Master of Puppets | 1986 | Rock, Metal | Thrash | None |
| Black Sabbath | Paranoid | 1970 | Rock | Heavy Metal | None |
| Daft Punk | Discovery | 2001 | Electronic | House | Yes (2 tracks) |

This gives: 4 genres (Jazz, Rock, Electronic, Metal), 4 decades (1950s, 1970s, 1980s, 2000s), 4 with tracklists, 2 without. Enough for all filter/search/detail tests.

### 1c. Playwright config update

**Modify:** `apps/frontend-e2e/playwright.config.ts`

- Set `TEST_MODE=true`, `HOST_PIN=1234`, `DATABASE_URL` (temp file path), and dummy `DISCOGS_TOKEN`/`DISCOGS_USERNAME` in `process.env` before config export
- Use Playwright's `webServer` array to start both backend and frontend:

```typescript
webServer: [
  {
    command: 'cd apps/backend && uv run alembic upgrade head && uv run uvicorn cue_the_music.main:app --port 8000',
    url: 'http://localhost:8000/api/albums',
    reuseExistingServer: true,
    cwd: workspaceRoot,
    timeout: 30_000,
    env: { ...process.env },
  },
  {
    command: 'npx nx run @cue-the-music/frontend:preview',
    url: 'http://localhost:4200',
    reuseExistingServer: true,
    cwd: workspaceRoot,
    timeout: 30_000,
  },
],
```

- Add mobile Safari project:

```typescript
{
  name: 'mobile-safari',
  use: { ...devices['iPhone 14'] },
},
```

### 1d. Global setup/teardown

**Create:** `apps/frontend-e2e/src/global-setup.ts`

Generate temp DB path, set `DATABASE_URL` env var. Write path to a temp file so teardown can find it.

**Create:** `apps/frontend-e2e/src/global-teardown.ts`

Delete the temp DB file (and `-shm`/`-wal` companions).

### 1e. Shared test fixture

**Create:** `apps/frontend-e2e/src/fixtures.ts`

A Playwright `test` fixture that calls `POST /api/test/reset` in `beforeAll` (via `request` API context). All test files import from this fixture instead of `@playwright/test`.

## Phase 2: Test Suites

### 2a. Guest collection browsing (`src/guest-browse.spec.ts`)

- Browse crate page — see album grid with seeded albums
- Search by artist name — results filter correctly
- Search by album title — results filter correctly
- Clear search — all albums return
- Filter by genre — matching albums shown
- Filter by decade — matching albums shown
- Combined genre + decade filter
- Album count updates with filters
- Toggle show/hide filters

### 2b. Album detail and request (`src/album-request.spec.ts`)

- Open album detail overlay — cover art, title, artist, tracklist visible
- Close overlay
- Request album — button shows "Requested", auto-closes to queue
- Return to crate — album shows "In Queue" button
- Cancel own request from queue

### 2c. Voting (`src/voting.spec.ts`)

- Upvote a queue item — count increments
- Downvote a queue item — count increments
- Toggle vote off — count decrements
- Requester's auto-upvote is visible

### 2d. Host mode (`src/host-mode.spec.ts`)

- Activate host mode with correct PIN
- Wrong PIN is rejected
- Promote to now playing — item moves from queue to now playing section
- Remove queue item — disappears from queue
- Clear all — queue and now playing emptied
- Deactivate host mode — host controls disappear

### 2e. Navigation (`src/navigation.spec.ts`)

- Tab switching between Crate and Queue
- Crate state (search, filters) persists across tab switches
- Album overlay closes on tab switch

## Acceptance Criteria

- [ ] `npx nx e2e @cue-the-music/frontend-e2e` runs all tests with zero manual setup (R1)
- [ ] Test-only reset endpoint mounted only when `TEST_MODE=true` (R2)
- [ ] Each test suite starts with clean, seeded data (R3)
- [ ] Temp DB created and deleted per test run (R4)
- [ ] All user journeys from R5 covered
- [ ] No Discogs sync tests (R6)
- [ ] Tests run on Chromium, mobile Chrome, WebKit, and mobile Safari (R7)
- [ ] Tests do not touch the dev/production database
- [ ] Backend tests still pass (`cd apps/backend && uv run pytest`)

## Deferred Questions Resolved

- **Seed data**: 6 albums, 4 genres, 4 decades, mix of tracklist states (see table above)
- **Starting both servers**: Playwright `webServer` array — backend first (with migrations), then frontend preview
- **Env vars**: Set in `playwright.config.ts` via `process.env` assignments before config export. Temp DB path generated in `global-setup.ts`.

## Sources

- **Origin document:** [docs/brainstorms/2026-03-27-playwright-e2e-tests-requirements.md](docs/brainstorms/2026-03-27-playwright-e2e-tests-requirements.md) — Key decisions: temp DB + reset endpoint, TEST_MODE guard, skip sync E2E, pre-seeded data
- `apps/frontend-e2e/playwright.config.ts` — existing Playwright config (webServer, projects)
- `apps/frontend-e2e/src/example.spec.ts` — existing smoke tests to replace
- `apps/backend/src/cue_the_music/main.py:70-104` — app factory where test router is conditionally mounted
- `apps/backend/src/cue_the_music/models/album.py` — Album model for seed data shape
