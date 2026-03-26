---
title: "fix: Persist original release year from Discogs master release"
type: fix
status: active
date: 2026-03-25
---

# fix: Persist original release year from Discogs master release

## Overview

The Discogs sync pipeline persists the **pressing/reissue year** instead of the **original release year**. A 2020 repress of a 1969 album displays as 2020. The fix fetches the master release for each album during sync and uses its `year` field, which represents the original release year.

## Problem Statement

`DiscogsBasicInformation` extracts `year` from the collection response, but this is the year of the specific pressing in the user's collection — not the original release. The Discogs collection endpoint returns `master_id` alongside `basic_information`, but it is silently dropped by `extra="ignore"`. No master release endpoint exists in the client.

This affects:
- Album year display throughout the app (Crate browse, album detail, queue items)
- Decade filter chips (a 1969 album filed under "2020s")
- The entire purpose of showing "year" — users expect the original release year

## Proposed Solution

### 1. Extract `master_id` from collection response

Add `master_id: int = 0` to `DiscogsCollectionRelease` (not `DiscogsBasicInformation` — `master_id` is a sibling of `basic_information` in the Discogs API response, not nested inside it).

```python
# discogs_client.py — DiscogsCollectionRelease
class DiscogsCollectionRelease(BaseModel):
    model_config = ConfigDict(extra="ignore")
    basic_information: DiscogsBasicInformation
    master_id: int = 0  # 0 means no master (unofficial/compilations)
```

### 2. Add `get_master_release()` to `DiscogsClient`

New method hitting `GET /masters/{master_id}`. Define a minimal response model:

```python
class DiscogsMasterRelease(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    year: int = 0
```

The method goes through the existing rate limiter — no new limiter needed.

### 3. Resolve original year during sync

In `sync_service.py`, add a `_resolve_year` helper:

```python
async def _resolve_year(
    self,
    master_id: int,
    release_year: int,
) -> int | None:
    """Resolve original release year from master, falling back to release year."""
    if master_id > 0:
        try:
            master = await self._client.get_master_release(master_id)
            if master.year > 0:
                return master.year
        except Exception:
            logger.warning("Failed to fetch master %d, using release year", master_id)
    return release_year if release_year > 0 else None
```

Call this in `_upsert_album` instead of the current `info.year if info.year else None`.

### 4. Add `discogs_master_id` column to Album model

Store the master ID so subsequent syncs can skip re-fetching masters whose years are already resolved. This requires an Alembic migration.

```python
# album.py
discogs_master_id: Mapped[int | None] = mapped_column(Integer)
```

The sync upsert logic becomes: if `existing.discogs_master_id == master_id` and `existing.year is not None`, skip the master fetch for that album.

### 5. No frontend changes needed

- Year display already reads from the `year` field — the value will simply be correct after re-sync
- Decade filters are computed dynamically from album years (`album_repository.py:122-130`)
- The `collection_sync` SSE event already triggers a cache refresh via `albumKeys.all` invalidation (`host-mutations.ts` `useTriggerSync.onSuccess`)
- Verify the SSE handler also invalidates `albumKeys.filters()` for decade chip refresh

## Technical Considerations

### Performance — sync duration

A 500-album collection currently takes ~5 API calls (paginated). Adding master fetches means up to 505 calls. At 50 req/min, that is ~10 minutes.

**Mitigations (ordered by priority):**

1. **Cache via `discogs_master_id`:** After the first sync, subsequent syncs skip master fetches for albums whose master year is already resolved. Only new albums need master lookups.
2. **Batch within pages:** Fetch masters for each page's albums before moving to the next page. This keeps the commit-per-page pattern from the SQLite learnings doc.
3. **Sync is already host-only and on-demand (R30).** The host explicitly triggers it and expects it to take time. The first sync being slow is acceptable; subsequent syncs are fast.

**Not in scope:** Making sync fully async/background. The current inline approach works for the expected collection sizes (500-1000 albums). If sync duration becomes a real problem, that's a separate enhancement.

### Error isolation

A single master fetch failure must NOT abort the entire sync. The `_resolve_year` helper catches exceptions per-album and falls back to the release year. This matches the existing pattern where sync continues through individual album failures.

### Rate limiter headroom

The existing `AsyncLimiter(max_rate=50, time_period=60)` is shared across all Discogs API calls. During a sync with master fetches, guest tracklist requests (`get_release_detail`) will compete for rate limit budget. This is acceptable — sync is a brief, infrequent operation and tracklist fetches are cached after first view (R32).

### SQLite concurrency

Per `docs/solutions/configuration-fixes/sqlite-async-fastapi-setup.md`: commit per page during sync, not one giant transaction. The existing sync service already follows this pattern. The master fetch adds latency within each page's processing but does not change the transaction boundaries.

### `master_id` location in Discogs API

The Discogs collection endpoint (`/users/{username}/collection/folders/0/releases`) returns:
```json
{
  "releases": [
    {
      "id": 123,
      "master_id": 456,        // ← sibling of basic_information
      "basic_information": {
        "year": 2020,           // ← pressing year
        "title": "Abbey Road",
        ...
      }
    }
  ]
}
```

`master_id` is on the release object, NOT inside `basic_information`. The field must be added to `DiscogsCollectionRelease`.

## Acceptance Criteria

- [ ] After sync, albums display their original release year (e.g., Abbey Road shows 1969, not 2020)
- [ ] Albums without a master (`master_id` absent or 0) fall back to the release pressing year
- [ ] Albums where both master year and release year are 0 display no year (`None`)
- [ ] A failed master fetch for one album does not abort the sync — falls back to release year with a warning log
- [ ] Subsequent syncs skip master fetches for albums whose `discogs_master_id` is already stored and year is resolved
- [ ] Decade filter chips update correctly after sync (1969 album appears under "1960s")
- [ ] Alembic migration adds `discogs_master_id` column to albums table
- [ ] OpenAPI schema regenerated; frontend types updated
- [ ] All existing backend tests pass; new tests cover `_resolve_year` logic

## Key Files

| File | Action | Purpose |
|------|--------|---------|
| `apps/backend/src/cue_the_music/integrations/discogs_client.py` | Modify | Add `master_id` to `DiscogsCollectionRelease`, add `DiscogsMasterRelease` model, add `get_master_release()` |
| `apps/backend/src/cue_the_music/services/sync_service.py` | Modify | Add `_resolve_year` helper, wire into `_upsert_album` |
| `apps/backend/src/cue_the_music/models/album.py` | Modify | Add `discogs_master_id` column |
| `apps/backend/alembic/versions/` | Create | Migration for `discogs_master_id` column |
| `apps/backend/src/cue_the_music/schemas/album_schemas.py` | Verify | No change expected — `year` field stays the same |
| `apps/backend/tests/` | Modify | Tests for `_resolve_year`, master fetch fallback, caching |

## Dependencies & Risks

- **Risk:** The Discogs collection API response structure for `master_id` must be verified against a real response. The plan assumes it's a sibling of `basic_information` based on SpecFlow analysis.
- **Risk:** First sync after the fix will be significantly slower (up to 10 minutes for 500 albums). Host should be informed this is a one-time cost.
- **Dependency:** Alembic migration must run before the sync service uses the new `discogs_master_id` column.
- **Dependency:** Frontend types must be regenerated from OpenAPI after backend schema changes (per `docs/solutions/runtime-errors/queue-view-crash-type-schema-divergence.md`).

## Sources

- **Learnings:** [docs/solutions/configuration-fixes/sqlite-async-fastapi-setup.md](docs/solutions/configuration-fixes/sqlite-async-fastapi-setup.md) — commit per page during sync
- **Learnings:** [docs/solutions/runtime-errors/queue-view-crash-type-schema-divergence.md](docs/solutions/runtime-errors/queue-view-crash-type-schema-divergence.md) — regenerate frontend types from OpenAPI
- **Learnings:** [docs/solutions/ui-bugs/host-controls-not-mounted-after-pin-verification.md](docs/solutions/ui-bugs/host-controls-not-mounted-after-pin-verification.md) — `useTriggerSync` onSuccess invalidation
- **Discogs API:** Master Release endpoint returns `year` as original release year; collection releases return pressing year
