---
title: "fix: Retain Crate tab search, filter, and UI state across tab switches"
type: fix
status: active
date: 2026-03-26
---

# fix: Retain Crate tab search, filter, and UI state across tab switches

## Problem

Switching from the Crate tab to the Queue tab and back resets search query, selected genre/decade filters, and filter visibility to their initial state. The state lives in `useState` hooks that reset when the component unmounts during route navigation.

## Proposed Solution

Move persistent crate UI state to a Zustand store. Per standards: "If state is shared across components that are not in a direct parent-child relationship, use Zustand."

### New: `useCrateStore`

**Create:** `libs/frontend/feature-crate/src/lib/store/crate-store.ts`

```typescript
import { create } from 'zustand';

interface ICrateState {
  isFiltersOpen: boolean;
  search: string;
  selectedDecades: string[];
  selectedGenres: string[];
  setIsFiltersOpen: (open: boolean) => void;
  setSearch: (search: string) => void;
  setSelectedDecades: (decades: string[]) => void;
  setSelectedGenres: (genres: string[]) => void;
  toggleFilters: () => void;
}

export const useCrateStore = create<ICrateState>((set) => ({
  isFiltersOpen: false,
  search: '',
  selectedDecades: [],
  selectedGenres: [],
  setIsFiltersOpen: (open) => set({ isFiltersOpen: open }),
  setSearch: (search) => set({ search }),
  setSelectedDecades: (selectedDecades) => set({ selectedDecades }),
  setSelectedGenres: (selectedGenres) => set({ selectedGenres }),
  toggleFilters: () => set((s) => ({ isFiltersOpen: !s.isFiltersOpen })),
}));
```

Export from barrel: `libs/frontend/feature-crate/src/lib/store/index.ts` and `libs/frontend/feature-crate/src/index.ts`.

### Modify: `useCrateView`

Replace `useState` for search, selectedGenres, selectedDecades with granular selectors from `useCrateStore`. Keep `selectedAlbumId` as local `useState` (overlay should reset on navigation).

### Modify: `useCollectionSearch`

Replace `useState` for `isFiltersOpen` with `useCrateStore` selector + `toggleFilters` action. Remove the `handleToggleFilters` callback wrapper.

### Modify: `useSearchInput` (SearchInput component)

The SearchInput needs to sync its local `inputValue` with the store's `search` value on mount. It already has a `value` prop for controlled mode — pass the store's search value via `CrateView` → `CollectionSearch` → `SearchInput`.

**Modify:** `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch-types.ts` — add `searchValue: string` prop.

**Modify:** `libs/frontend/feature-crate/src/lib/CrateView/CrateView.tsx` — pass `searchValue={filters.search ?? ''}` to CollectionSearch.

**Modify:** `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch.tsx` — pass `value={searchValue}` to SearchInput.

## Acceptance Criteria

- [ ] Search query persists when switching to Queue and back
- [ ] Selected genres persist across tab switches
- [ ] Selected decades persist across tab switches
- [ ] Filter show/hide state persists across tab switches
- [ ] Album detail overlay resets (closes) on tab switch (intentional)
- [ ] Granular selectors used (no full-store subscriptions)
- [ ] No `persist` middleware (no need to survive page refresh)

## Sources

- `libs/frontend/feature-crate/src/lib/CrateView/useCrateView.ts` — search/filter useState
- `libs/frontend/feature-crate/src/lib/CollectionSearch/useCollectionSearch.ts` — isFiltersOpen useState
- `docs/standards/STANDARDS-frontend.md:61` — Zustand for cross-component state
- `libs/frontend/feature-host/src/lib/store/host-store.ts` — existing Zustand store pattern
