---
title: "feat: Genre filter hybrid chip + modal UX"
type: feat
status: completed
date: 2026-03-25
origin: docs/brainstorms/2026-03-25-genre-filter-ux-requirements.md
---

# feat: Genre filter hybrid chip + modal UX

## Overview

Replace the full genre chip list on the crate page with a compact hybrid UI: top 3 genres by album count shown as chips, a "More" button opening a modal with all ~100 genres, and a two-state display that swaps between default and active selection views.

## Problem Statement

The crate page renders ~100 genre chips in a flex-wrap layout, pushing the album grid far below the fold. Guests must scroll past a wall of buttons before seeing any records. (see origin: `docs/brainstorms/2026-03-25-genre-filter-ux-requirements.md`)

## Proposed Solution

Two-state genre filter bar with modal picker:

**Default state (no selections):** Top 3 genre chips (by album count) + "More" button
**Active selection state:** Selected genre chips + "More" button + "Clear" button

The "More" button opens a Dialog modal containing all genres as toggleable chips, sorted by album count descending. Selections apply immediately on toggle. The existing `Dialog` component from `core-ui` is reused.

### Key Design Decisions (from origin)

- **Top 3 by album count** — dynamically determined, adapts as collection changes
- **Modal over popover/dropdown** — ~100 genres warrants full modal; reuse existing chip style
- **Replace, don't augment** — active selections replace the default view to keep filter area compact
- **"More" persists in both states** — ensures users can always open the modal to modify selections (gap identified by SpecFlow analysis)

### Interaction Details

- **Top-3 chips are direct toggles** — tapping a chip immediately filters the grid (1 tap)
- **Modal selections apply immediately** — no "Done" button; closing the modal just dismisses the picker
- **Genre sort in modal** — by album count descending (popular genres first)
- **"More" button styling** — outlined/ghost variant to visually distinguish from selectable genre chips
- **"Clear" button** — removes all genre selections, restores default state
- **Overflow handling** — if selected chips exceed one row, use horizontal scroll (`overflow-x: auto`) with fade hint. This preserves visibility of all selections without truncation.
- **AND logic retained** — multiple genre selections use existing AND filtering (all genres must match)

## Technical Approach

### Phase 1: Backend — Add genre counts to filter response

The current `GET /api/album-filters` returns a flat `genres: list[str]`. To determine the top 3, we need album counts per genre. This is a minor scope expansion from the origin doc's "no backend changes" boundary, but it's the cleanest approach — having the frontend compute counts from album data would require fetching all albums.

**Files to modify:**

| File | Change |
|------|--------|
| `apps/backend/src/cue_the_music/repositories/album_repository.py` | Modify `get_filters()` query to return `(genre, count)` pairs using `COUNT` + `GROUP BY` on `json_each()` |
| `apps/backend/src/cue_the_music/schemas/album_schemas.py` | Add `GenreCount` schema (`genre: str`, `count: int`). Change `AlbumFilterGetResponse.genres` from `list[str]` to `list[GenreCount]` |
| `apps/backend/src/cue_the_music/routers/album_router.py` | No changes needed (schema handles serialization) |

After schema change: regenerate OpenAPI types → update `@cue-the-music/core-types`.

### Phase 2: Frontend — New GenreFilter component

Create a new `GenreFilter` component in `libs/frontend/feature-crate/src/lib/GenreFilter/` following project conventions:

| File | Purpose |
|------|---------|
| `index.ts` | Public export |
| `GenreFilter.tsx` | Component — renders chip bar (default or active state) |
| `GenreFilter-elements.ts` | Panda CSS styles — chip row, overflow scroll, more/clear buttons |
| `GenreFilter-types.ts` | `IGenreFilterProps`, `IUseGenreFilterReturn` |
| `useGenreFilter.ts` | Hook — manages modal open state, derives top-3 from counted genres, handles toggle/clear |
| `GenreFilterModal.tsx` | Sub-component — Dialog with all genre chips, reuses existing chip styling |
| `GenreFilterModal-elements.ts` | Modal-specific styles (chip grid layout within dialog) |
| `GenreFilterModal-types.ts` | `IGenreFilterModalProps` |

**Component API:**

```typescript
interface IGenreFilterProps {
  genres: GenreCount[];           // from API, sorted by count desc
  selectedGenres: string[];
  onSelectionChange: (selected: string[]) => void;
}
```

**Default state rendering:**
```
[Rock] [Jazz] [Electronic] [+ More]
```

**Active selection state rendering:**
```
[Rock] [Funk] [+ More] [✕ Clear]
```

**GenreFilterModal rendering:**
```
┌─────────────────────────────────┐
│  Browse Genres              ✕   │
│                                 │
│  [Rock 42] [Jazz 38] [Elec 35] │
│  [Funk 28] [Soul 24] [Hip  21] │
│  ... all ~100 genres as chips   │
│                                 │
└─────────────────────────────────┘
```

### Phase 3: Integration

**Files to modify:**

| File | Change |
|------|--------|
| `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch.tsx` | Replace `ChipFilter` for genres with `GenreFilter` |
| `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch-types.ts` | Update props to accept `GenreCount[]` instead of `string[]` for genres |
| `libs/frontend/feature-crate/src/lib/CrateView/CrateView.tsx` | Pass `GenreCount[]` from `useAlbumFilters()` to `CollectionSearch` |
| `libs/frontend/data-access-collection/src/lib/album-queries.ts` | Update query/types if needed for new schema shape |

### Phase 4: Accessibility

- Add `aria-pressed={isSelected}` to all chip buttons (in both GenreFilter and the existing ChipFilter used for decades)
- Ensure modal has proper focus trap (already handled by ark-ui Dialog)
- "More" and "Clear" buttons need descriptive `aria-label` attributes

## Acceptance Criteria

- [ ] `GET /api/album-filters` returns genres with album counts, sorted by count descending
- [ ] Default state shows top 3 genre chips + "More" button in a single row
- [ ] Tapping a top-3 chip immediately filters the album grid
- [ ] Tapping "More" opens a modal with all genres as toggleable chips
- [ ] Modal shows genres sorted by album count; selected genres are visually distinct
- [ ] Closing modal updates the chip bar to active selection state
- [ ] Active state shows selected chips + "More" + "Clear" in a single row
- [ ] "Clear" removes all genre selections and restores default state
- [ ] Chip row uses horizontal scroll if selections overflow one row
- [ ] Decade filter remains unchanged
- [ ] Chip buttons have `aria-pressed` attribute
- [ ] All new components follow project folder anatomy conventions
- [ ] Generated types updated from OpenAPI schema change

## Dependencies & Risks

- **OpenAPI type regeneration** — backend schema change requires regenerating frontend types. Follow the pattern from `core-types` lib.
- **Panda CSS in feature lib** — per learnings, externalize `@styled-system` imports in Vite config (see `docs/solutions/build-errors/nx-panda-css-circular-dependency.md`).
- **Nullable genre_tags** — per learnings, use null-safe access (`?? []`) for genre/style tags (see `docs/solutions/runtime-errors/queue-view-crash-type-schema-divergence.md`).

## Sources & References

- **Origin document:** [docs/brainstorms/2026-03-25-genre-filter-ux-requirements.md](../brainstorms/2026-03-25-genre-filter-ux-requirements.md) — Key decisions: top-3 by count, modal for full list, replace-not-augment active state
- **SpecFlow analysis:** [docs/specs/genre-filter-ux-analysis.md](../specs/genre-filter-ux-analysis.md) — Identified "More" persistence gap, overflow handling, accessibility needs
- Existing Dialog: `libs/frontend/core-ui/src/lib/Dialog/Dialog.tsx`
- Existing ChipFilter: `libs/frontend/feature-crate/src/lib/ChipFilter/ChipFilter.tsx`
- Album repository: `apps/backend/src/cue_the_music/repositories/album_repository.py:100-130`
- Frontend standards: `docs/standards/STANDARDS-frontend.md`
