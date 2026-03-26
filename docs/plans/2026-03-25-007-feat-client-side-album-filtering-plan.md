---
title: "feat: Client-side album filtering and search"
type: feat
status: completed
date: 2026-03-25
---

# feat: Client-side album filtering and search

## Overview

Move album filtering and search from server-side API calls to client-side in-memory operations. Since all albums are already loaded on page load, every filter/search change currently triggers a redundant network round-trip. Client-side filtering eliminates this latency entirely, making the browse experience feel instant.

## Problem Statement

Every search keystroke (after debounce) and every filter toggle fires `GET /api/albums?search=...&genre=...&decade=...`, hitting the database each time. The full album set is small enough to hold in memory (a personal vinyl collection), so this network overhead is unnecessary and makes filtering feel sluggish.

## Proposed Solution

1. Fetch **all albums once** with no filter params and cache them in TanStack Query
2. Derive available filter values (genres with counts, decades) from the full album set client-side
3. Apply search and filter predicates in-memory using `useMemo`
4. Keep all existing UI components unchanged (GenreFilter, ChipFilter, SearchInput)
5. Remove server-side filter endpoints and backend filter logic as dead code cleanup

### Filter Semantics

- **Within a category**: OR logic. Selecting decades 1970 and 2010 shows albums from **both** decades
- **Across categories**: AND logic. If genre "Jazz" and decade "1970" are both selected, albums must match **at least one selected genre AND fall within at least one selected decade**
- **Search + filters**: AND logic. Search narrows within the filtered set

### Null Value Handling

- Albums with `year: null` are **excluded** when any decade filter is active (no decade to match against). They appear normally when no decade filter is set. This matches current server-side behavior.
- Albums with null/empty `genre_tags` and `style_tags` are **excluded** when any genre filter is active. They appear normally when no genre filter is set.

### Genre Count Display

- Genre counts are **static** — derived from the full unfiltered album set, not reactive to active filters. This maintains the current UX and avoids confusing count changes as filters toggle.

## Technical Approach

### Phase 1: Client-side filter utility library

Create a pure utility module in `libs/frontend/data-access-collection/` with filtering functions and comprehensive tests.

**New file:** `libs/frontend/data-access-collection/src/lib/album-filters.ts`

```typescript
import type { IAlbum, IAlbumFilterValues, IGenreCount } from '@cue-the-music/core-types';

/** Derive available filter values (genres with counts, decades) from the full album set. */
export function deriveFilterValues(albums: IAlbum[]): IAlbumFilterValues {
  // Count genres across both genre_tags and style_tags
  const genreCounts = new Map<string, number>();
  for (const album of albums) {
    const allTags = [...(album.genre_tags ?? []), ...(album.style_tags ?? [])];
    const unique = new Set(allTags);
    for (const tag of unique) {
      genreCounts.set(tag, (genreCounts.get(tag) ?? 0) + 1);
    }
  }

  const genres: IGenreCount[] = [...genreCounts.entries()]
    .map(([genre, count]) => ({ count, genre }))
    .sort((a, b) => b.count - a.count || a.genre.localeCompare(b.genre));

  const decadeSet = new Set<number>();
  for (const album of albums) {
    if (album.year != null) {
      decadeSet.add(Math.floor(album.year / 10) * 10);
    }
  }
  const decades = [...decadeSet].sort((a, b) => a - b);

  return { decades, genres };
}

/** Filter albums by search text, genres, and decades (all client-side). */
export function filterAlbums(
  albums: IAlbum[],
  filters: { decades?: string[]; genres?: string[]; search?: string },
): IAlbum[] {
  return albums.filter((album) => {
    // Search: case-insensitive match on artist or title
    if (filters.search) {
      const term = filters.search.toLowerCase();
      if (
        !album.artist.toLowerCase().includes(term) &&
        !album.title.toLowerCase().includes(term)
      ) {
        return false;
      }
    }

    // Genre filter (OR): album must have at least one matching genre/style tag
    if (filters.genres?.length) {
      const albumTags = [
        ...(album.genre_tags ?? []),
        ...(album.style_tags ?? []),
      ];
      if (!filters.genres.some((g) => albumTags.includes(g))) {
        return false;
      }
    }

    // Decade filter (OR): album.year must fall within at least one selected decade
    if (filters.decades?.length) {
      if (album.year == null) return false;
      const albumDecade = Math.floor(album.year / 10) * 10;
      if (!filters.decades.some((d) => Number(d) === albumDecade)) {
        return false;
      }
    }

    return true;
  });
}
```

**New file:** `libs/frontend/data-access-collection/src/lib/album-filters.spec.ts`

Tests covering:

- Empty album list returns empty results and empty filter values
- Search matches artist (case-insensitive)
- Search matches title (case-insensitive)
- Search with no match returns empty
- Single genre filter matches `genre_tags`
- Single genre filter matches `style_tags`
- Multi-genre filter uses OR logic (matches either)
- Genre filter excludes albums with null/empty tags
- Single decade filter matches correct year range
- Multi-decade filter uses OR logic
- Decade filter excludes albums with `year: null`
- Combined genre + decade uses AND across categories
- Combined search + filters uses AND
- `deriveFilterValues` counts genres across both tag arrays
- `deriveFilterValues` deduplicates genres within a single album
- `deriveFilterValues` sorts genres by count desc, then name asc
- `deriveFilterValues` computes decades sorted ascending
- `deriveFilterValues` excludes null years from decades

### Phase 2: Rewire data-access hooks

**Modify:** `libs/frontend/data-access-collection/src/lib/album-queries.ts`

1. Change `useAlbums()` to always fetch with **no filter params** (single cache entry for all albums)
2. Remove `buildFilterParams()` — no longer needed
3. Remove `albumListQueryOptions(filters)` filter param — query key becomes just `albumKeys.all`
4. Remove `useAlbumFilters()` hook — filter values will be derived client-side
5. Remove `albumFiltersQueryOptions()` — no longer needed
6. Simplify query key factory: remove `albumKeys.list(filters)` variant, keep `albumKeys.lists()` for cache lookup in `useAlbum()`
7. Export new hooks:

```typescript
/** Fetch all albums (unfiltered). */
export function useAllAlbums() {
  return useSuspenseQuery(albumListQueryOptions());
}
```

**Update barrel exports** to remove `useAlbumFilters`, add `useAllAlbums`, and export `filterAlbums` / `deriveFilterValues`.

### Phase 3: Update CrateView wiring

**Modify:** `libs/frontend/feature-crate/src/lib/CrateView/useCrateView.ts`

- Import `filterAlbums` and `deriveFilterValues`
- Accept the full album list as input (or call `useAllAlbums` directly — but per standards, hooks shouldn't call data-access hooks; the component orchestrates)
- Add `useMemo` to compute filtered albums and derived filter values
- Reduce search debounce: since filtering is now in-memory, reduce `SearchInput` debounce from 300ms to 150ms (or remove entirely — `useMemo` is fast enough for thousands of albums)

**Modify:** `libs/frontend/feature-crate/src/lib/CrateView/CrateView.tsx`

```typescript
export function CrateView(props: ICrateViewProps) {
  const {
    filters,
    handleCloseOverlay,
    handleDecadesChange,
    handleGenresChange,
    handleOpenOverlay,
    handleSearch,
    selectedAlbumId,
  } = useCrateView(props);

  const { data: albumData } = useAllAlbums();

  const allAlbums = albumData.albums;
  const filteredAlbums = useMemo(
    () => filterAlbums(allAlbums, filters),
    [allAlbums, filters],
  );
  const filterValues = useMemo(
    () => deriveFilterValues(allAlbums),
    [allAlbums],
  );

  const hasNoCollection = allAlbums.length === 0;
  const hasActiveFilters = !!(filters.search || filters.genres || filters.decades);
  const hasNoResults = filteredAlbums.length === 0 && !hasNoCollection;

  // ... rest unchanged, use filteredAlbums instead of albums
}
```

### Phase 4: Backend cleanup

**Modify:** `apps/backend/src/cue_the_music/routers/album_router.py`

- Remove `search`, `genre`, `decade` query parameters from the `GET /api/albums` endpoint
- Keep the endpoint returning all albums (it already does when no filters are passed)

**Decide:** Remove or keep `GET /api/album-filters` endpoint.
- **Recommendation:** Remove it. Filter values are now derived client-side. Dead endpoints are a maintenance burden.

**Modify:** `apps/backend/src/cue_the_music/repositories/album_repository.py`

- Simplify `get_all()` to remove filter parameters and filter logic
- Remove `get_filters()` method

**Modify:** `apps/backend/src/cue_the_music/services/album_service.py`

- Simplify corresponding service methods

**Regenerate frontend types** from the updated OpenAPI schema after backend changes.

### Phase 5: Update backend tests

- Update/remove tests that exercise server-side filter parameters
- Ensure `get_all()` still returns all albums sorted by artist, title

## Acceptance Criteria

### Functional

- [ ] All albums load in a single API call with no filter parameters
- [ ] Search filters albums by artist or title (case-insensitive, client-side)
- [ ] Genre filter supports multi-select with OR logic across `genre_tags` and `style_tags`
- [ ] Decade filter supports multi-select with OR logic
- [ ] Cross-category filters use AND logic (genre AND decade AND search)
- [ ] Albums with `year: null` excluded only when decade filter is active
- [ ] Albums with null/empty genre/style tags excluded only when genre filter is active
- [ ] Genre counts in filter chips are static (derived from full set, not reactive)
- [ ] "No albums match" empty state still works correctly
- [ ] "No albums yet" empty state triggers only when collection is truly empty
- [ ] Album detail overlay still works (cache lookup unchanged)
- [ ] Existing GenreFilter hybrid chip+modal UX unchanged
- [ ] Existing ChipFilter decade UX unchanged

### Non-Functional

- [ ] Filtering feels instant (< 16ms for `useMemo` on collections up to 5,000 albums)
- [ ] No unnecessary re-renders — `useMemo` deps are stable
- [ ] `filterAlbums` and `deriveFilterValues` have unit tests with 90%+ coverage
- [ ] Backend filter query params removed from OpenAPI schema
- [ ] Frontend types regenerated from updated schema

### Quality Gates

- [ ] `npx nx run-many -t test` passes
- [ ] `npx nx typecheck @cue-the-music/frontend` passes
- [ ] `cd apps/backend && uv run pytest` passes

## Implementation Order

1. **`album-filters.ts` + `album-filters.spec.ts`** — pure functions with tests, zero risk
2. **`album-queries.ts`** — rewire hooks to fetch unfiltered, export new utilities
3. **`useCrateView.ts` + `CrateView.tsx`** — swap to client-side filtering
4. **Backend endpoint/repo/service cleanup** — remove dead filter code
5. **Regenerate frontend types** — update OpenAPI schema types
6. **Backend test updates** — remove server-side filter test cases

## Sources

### Internal References

- `libs/frontend/data-access-collection/src/lib/album-queries.ts` — current server-side query hooks
- `libs/frontend/feature-crate/src/lib/CrateView/useCrateView.ts` — current filter state management
- `libs/frontend/feature-crate/src/lib/CrateView/CrateView.tsx` — main view orchestration
- `libs/frontend/core-types/src/lib/album.ts` — TypeScript album types (generated from OpenAPI)
- `apps/backend/src/cue_the_music/repositories/album_repository.py` — server-side filter logic (to be removed)
- `libs/frontend/feature-crate/src/lib/GenreFilter/GenreFilter.tsx` — hybrid chip+modal UX (unchanged)
- `libs/frontend/feature-crate/src/lib/ChipFilter/ChipFilter.tsx` — decade chip filter (unchanged)
- `libs/frontend/core-ui/src/lib/SearchInput/useSearchInput.ts` — debounce implementation (configurable `debounceMs`)
