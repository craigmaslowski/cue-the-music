---
title: "feat: Collapsible filter section with toggle button"
type: feat
status: active
date: 2026-03-25
---

# feat: Collapsible filter section with toggle button

Add a toggle button between the search input and filter chips that collapses/expands the genre and decade filters. Button shows "Show Filters" / "Hide Filters" with a Material Symbols icon (expand_more / expand_less).

## Proposed Solution

**Modify:** `libs/frontend/feature-crate/src/lib/CollectionSearch/useCollectionSearch.ts`

- Add `isFiltersOpen` state (default: `true`)
- Add `handleToggleFilters` callback
- Return both in hook return type

**Modify:** `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch-types.ts`

- Add `handleToggleFilters` and `isFiltersOpen` to `IUseCollectionSearchReturn`

**Modify:** `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch.tsx`

- Render toggle button between search and filters
- Conditionally render the `filtersStyles` div based on `isFiltersOpen`
- Album count stays visible regardless of collapse state

**Modify:** `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch-elements.ts`

- Add `toggleButtonStyles` — transparent, muted text, flex with icon, small font

## Acceptance Criteria

- [ ] Toggle button visible between search input and filter chips
- [ ] Shows "Hide Filters" with expand_less icon when filters visible
- [ ] Shows "Show Filters" with expand_more icon when filters hidden
- [ ] Album count remains visible when filters collapsed
- [ ] Filters default to expanded on initial load
