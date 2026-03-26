---
title: "feat: Retrieve and persist tracklist during Discogs sync"
type: feat
status: active
date: 2026-03-25
---

# feat: Retrieve and persist tracklist during Discogs sync

## Overview

During collection sync, extract the tracklist from the master release response (already fetched for year resolution) and persist it alongside album metadata. This eliminates the lazy-fetch on album detail view for most albums, making tracklist display instant.

## Problem Statement

Currently tracklist is `NULL` after sync and only fetched on-demand when a user opens the album detail overlay. Each detail view triggers a Discogs API call (`GET /releases/{id}`), which is slow (rate-limited to 1 req/1.2s) and redundant — the master release we already fetch during sync contains the same tracklist.

## Proposed Solution

Piggyback on the existing master release fetch during sync — extract `tracklist` from the `DiscogsMasterRelease` response and persist it during upsert. **Zero additional API calls.**

### Rate Limiting Impact

| Phase | Current | Proposed |
|-------|---------|----------|
| Sync (per page) | 1 collection + N master fetches | **Same** — just extract more data from existing response |
| Album detail view | 1 release detail fetch (if tracklist null) | **None** for albums with master — tracklist already cached |
| API calls per album | Master fetch only | **Same master fetch** — tracklist extracted from same response |

**Discogs limits**: 60 req/min authenticated. Current limiter: 1 req/1.2s (50 req/min). No change to call volume.

### Albums without master_id

Albums with `master_id=0` have no master release to fetch — their tracklist stays `NULL` during sync. The existing lazy-fetch on album detail view (via `get_release_detail`) continues to work as fallback.

## Technical Approach

### 1. Extend `DiscogsMasterRelease` model

**Modify:** `apps/backend/src/cue_the_music/integrations/discogs_client.py`

Add `tracklist` field to `DiscogsMasterRelease`:

```python
class DiscogsMasterRelease(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    tracklist: list[DiscogsTrack] = []
    year: int = 0
```

### 2. Return tracklist from year resolution

**Modify:** `apps/backend/src/cue_the_music/services/sync_service.py`

Change `_resolve_years_for_page` return type to include tracklist data:

- Change `resolved_years: dict[str, int | None]` → `resolved_data: dict[str, ResolvedMasterData]` where `ResolvedMasterData` is a dataclass with `year: int | None` and `tracklist: list[dict] | None`
- In `_resolve_year`, also return the parsed tracklist (filter heading type tracks, same logic as `album_service._fetch_and_cache_tracklist`)
- Pass resolved tracklist to `_upsert_album`

### 3. Persist tracklist during upsert

**Modify:** `apps/backend/src/cue_the_music/services/sync_service.py` — `_upsert_album`

- On **insert**: set `tracklist` from resolved master data (or `None` if no master)
- On **update**: set `tracklist` from resolved master data only if the existing tracklist is `None` (don't overwrite a tracklist that was already lazy-fetched from the release endpoint, which may be more accurate for the specific pressing)

### 4. Skip re-fetch optimization

In `_resolve_years_for_page`, when checking the DB cache:
- If album already has `tracklist IS NOT NULL` AND `year` is resolved AND `master_id` matches → skip the master fetch entirely (same as current year caching, but now also checks tracklist)

### 5. Update tests

**Modify:** `apps/backend/tests/test_sync_service.py`

- Verify tracklist is persisted after sync for albums with master releases
- Verify tracklist stays `NULL` for albums without master_id
- Verify existing tracklist is NOT overwritten on re-sync
- Verify the caching optimization skips master fetch when year + tracklist already present

## Acceptance Criteria

- [ ] Albums synced with a master release have tracklist populated (not NULL)
- [ ] Albums without a master_id still have tracklist=NULL (lazy-fetch fallback works)
- [ ] Re-sync does not overwrite existing tracklist
- [ ] No additional Discogs API calls compared to current sync
- [ ] Rate limiting unchanged (1 req/1.2s, 50 req/min)
- [ ] Album detail overlay still lazy-fetches tracklist for NULL tracklist albums
- [ ] `cd apps/backend && uv run pytest` passes
- [ ] Heading-type tracks filtered from tracklist (consistent with existing lazy-fetch logic)

## Sources

- `apps/backend/src/cue_the_music/integrations/discogs_client.py:119-126` — DiscogsMasterRelease model (currently ignores tracklist)
- `apps/backend/src/cue_the_music/services/sync_service.py:98-156` — two-phase page processing + year resolution
- `apps/backend/src/cue_the_music/services/album_service.py:50-70` — existing tracklist lazy-fetch logic (heading filter)
- `docs/solutions/integration-issues/discogs-master-release-year-resolution.md` — rate limiting learnings
