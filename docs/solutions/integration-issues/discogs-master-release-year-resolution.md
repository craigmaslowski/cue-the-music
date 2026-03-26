---
title: "Discogs sync persists pressing year instead of original release year"
category: integration-issues
date: 2026-03-25
severity: high
component: "SyncService, DiscogsClient, DiscogsBasicInformation"
tags: [discogs, sync, master-release, year, rate-limiting, pydantic, aiolimiter, async-transaction]
related_issues: []
---

# Discogs sync persists pressing year instead of original release year

## Problem

After syncing a Discogs collection, albums displayed the pressing/reissue year instead of the original release year. For example, a 2016 repress of Black Sabbath's "Master of Reality" (originally 1971) showed as 2016.

## Root Cause (Three Layers)

### 1. No master release lookup

The Discogs collection endpoint (`/users/{username}/collection/folders/0/releases`) returns `basic_information.year` — the year of the **specific pressing** in the user's collection. The original release year is only available from the master release endpoint (`/masters/{master_id}`). The sync service had no master release support.

### 2. `master_id` on the wrong Pydantic model

The initial fix placed `master_id` on `DiscogsCollectionRelease` (top-level release object). But the Discogs API nests `master_id` **inside** `basic_information`, not as a sibling:

```json
{
  "id": 18648667,
  "basic_information": {
    "master_id": 2051947,  // ← HERE, not at the top level
    "year": 2016,
    "title": "Master Of Reality"
  }
}
```

Since `DiscogsBasicInformation` uses `extra="ignore"`, the field was silently dropped and every album got `master_id=0`.

**How we found it:** Queried the DB after sync — `discogs_master_id` was `None` for all albums. Then hit the actual Discogs API and printed the raw JSON structure to confirm `master_id` lives inside `basic_information`.

### 3. API calls inside DB transaction caused failures

Master release fetches happened inside `async with session.begin()`, holding the SQLite write lock during rate-limited HTTP calls. With 100 releases per page, this caused timeouts/failures on every master fetch.

### 4. Rate limiter allowed bursting

`AsyncLimiter(max_rate=50, time_period=60)` allows a **burst of 50 requests at once**, then throttles. Discogs rejects these bursts with 429s even though the average rate is within limits.

## Solution

### Fix 1: Move `master_id` to correct model

```python
# discogs_client.py — DiscogsBasicInformation (NOT DiscogsCollectionRelease)
class DiscogsBasicInformation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    # ... other fields ...
    master_id: int = 0  # ← inside basic_information where Discogs puts it
```

### Fix 2: Two-phase page processing

Resolve master years **outside** the DB transaction:

```python
async def _upsert_page(self, releases):
    # Phase 1: HTTP calls (no DB lock)
    resolved_years = await self._resolve_years_for_page(releases)

    # Phase 2: DB writes (no HTTP calls)
    async with async_session_factory() as session, session.begin():
        for release in releases:
            await self._upsert_album(session, release, resolved_years[...])
```

### Fix 3: Prevent rate limiter bursting

```python
# Before: allows burst of 50, then throttles
_rate_limiter = AsyncLimiter(max_rate=50, time_period=60)

# After: 1 request per 1.2s ≈ 50 req/min, no burst
_rate_limiter = AsyncLimiter(max_rate=1, time_period=1.2)
```

### Fix 4: Cache master_id to skip re-fetches

Added `discogs_master_id` column to Album model. On subsequent syncs, if the album's `discogs_master_id` matches and `year` is set, the master fetch is skipped.

## Key Gotchas

1. **Always verify Discogs API response structure with real data.** The SpecFlow analysis incorrectly assumed `master_id` was a sibling of `basic_information`. A single `print(release.keys())` against the live API would have caught this immediately.

2. **Never make HTTP calls inside a DB transaction.** Rate-limited APIs + DB write locks = guaranteed failures. Separate the I/O phases.

3. **`aiolimiter` burst behavior:** `AsyncLimiter(max_rate=N, time_period=T)` allows a burst of N requests, then refills over T seconds. For APIs that reject bursts, use `AsyncLimiter(1, T/N)` to enforce even spacing.

4. **Pydantic `extra="ignore"` silently drops unknown fields.** If a field is missing from the model, it won't error — it just won't be there. Verify field presence with real API responses, not assumptions.

## Prevention

- When integrating with external APIs, write a throwaway script that prints the raw response structure before building Pydantic models
- Separate HTTP I/O from DB transactions as a rule, not an optimization
- Test rate limiters against the real API during development, not just in unit tests with mocks
- For `aiolimiter`, prefer `AsyncLimiter(1, interval)` over `AsyncLimiter(N, period)` when the target API is burst-sensitive

## Related Solutions

- [SQLite async config](../configuration-fixes/sqlite-async-fastapi-setup.md) — commit per page during sync, WAL mode
- [API fetch headers / CORS](../integration-issues/api-fetch-headers-cors-lan-access.md) — Discogs auth header patterns

## Plan Reference

- [docs/plans/2026-03-25-005-fix-persist-original-release-year-from-discogs-plan.md](../../plans/2026-03-25-005-fix-persist-original-release-year-from-discogs-plan.md)
