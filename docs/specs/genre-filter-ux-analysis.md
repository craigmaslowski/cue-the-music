# Genre Filter UX Improvement -- Spec Analysis

## Codebase Context

**Current implementation**: `ChipFilter` renders ALL options as `flexWrap` chips (confirmed in `ChipFilter-elements.ts` line 21). With ~100 genres this pushes the album grid far below the fold -- the core problem this spec solves.

**Key existing patterns**:
- `Dialog` component (ark-ui based, in `core-ui`) is available for the modal
- Genre data comes from `get_filters()` which returns alphabetically sorted unique genre+style tags -- there is **no album count per genre** in the current API
- Genre filtering uses AND logic (all selected genres must match) per `album_repository.py` lines 48-66
- `ChipFilter` already supports multi-select toggle; `useChipFilter` manages selection state

**Affected files**: `ChipFilter/`, `CollectionSearch/`, `useCrateView.ts`, and the backend `album_repository.py` (for counts)

---

## User Flows

### Flow 1: Default State (no genres selected)
Guest sees search bar, then genre row showing top 3 chips + "More" button, then decade chips, then album grid.

### Flow 2: Quick Filter via Top-3 Chip
1. Guest taps a visible top-3 genre chip
2. View transitions to **active selection state**: chip row shows only selected chip + "Clear" button
3. Album grid re-filters immediately
4. Guest can tap the selected chip again to deselect it (returns to default state)

### Flow 3: Modal Browse and Select
1. Guest taps "More"
2. Modal opens showing all ~100 genres as chips
3. Guest taps one or more genres (chips toggle on/off)
4. Guest closes modal (X button, backdrop tap, or implicit "Done")
5. View transitions to active selection state with selected chips + "Clear"

### Flow 4: Modify Selection (re-open modal)
1. Guest is in active selection state, taps "More" (or a chip? -- see Gap 2)
2. Modal opens with current selections pre-checked
3. Guest adds/removes genres
4. Guest closes modal; chip row updates

### Flow 5: Clear All
1. Guest taps "Clear"
2. All genre selections removed
3. View returns to default state (top-3 + "More")

---

## Gaps

### Critical

**1. Backend does not return genre counts.**
R1 says "top 3 genres by album count." The current `get_filters()` endpoint returns only a flat sorted list of genre strings -- no album counts. This requires a backend change: either a new endpoint or modifying `AlbumFilterGetResponse` to include counts. Without this, the frontend cannot determine the top 3.

*Default assumption*: Modify `get_filters()` to return `list[{genre: str, count: int}]` sorted by count descending. This is a schema change that affects the generated OpenAPI types.

### Important

**2. How does the user add more genres when already in active selection state?**
The spec says "selected genre chips + Clear button" replaces the default view. But there is no affordance described for opening the modal again to add more genres. Should there be a "+" button, or does "More" persist in active state? If the user selects "Jazz" via a top-3 chip, how do they add "Funk" without first seeing the modal?

*Default assumption*: Show selected chips + "More" + "Clear" in active state.

**3. One-row constraint with variable chip widths.**
The spec says "genre filter area never exceeds one row." Genre names vary wildly in length ("UK Garage" vs "Post-Punk" vs "Contemporary R&B"). If a user selects 5+ genres, the selected chips + Clear + More could exceed one row on a 320px mobile screen. The spec does not define overflow behavior.

*Options*: (a) horizontal scroll with `overflow-x: auto`, (b) truncate with "+N more" count chip, (c) limit visible selected chips. Option (b) is most consistent with the spec's intent.

*Default assumption*: Show first N selected chips that fit, then a "+X" count chip, then Clear.

**4. Does tapping a top-3 chip apply immediately or open the modal?**
The spec says "no more than 2 taps" and that the top-3 are shown as chips. The natural UX is that tapping a top-3 chip toggles it directly (like today's ChipFilter behavior). But this is not explicit. If top-3 chips are selection toggles, what about multi-select -- can a guest tap Rock AND Jazz from the top-3 without opening the modal?

*Default assumption*: Top-3 chips are direct toggles (1 tap to filter). Multi-select from top-3 is allowed.

**5. AND vs OR logic not specified.**
The current backend applies AND logic (album must match ALL selected genres). With the new UX encouraging multi-genre selection, AND may produce empty results (few albums are both "Jazz" AND "Electronic"). Should this be changed to OR (album matches ANY selected genre)?

*Default assumption*: Keep AND logic since it matches existing behavior, but this should be validated with real data. If typical genres are very specific, AND will frustrate users.

### Minor

**6. Genre sort order in modal.**
The current API returns alphabetically sorted genres. With ~100 genres, alphabetical is reasonable. But should popular genres (by count) appear first, with a secondary alphabetical sort? The spec is silent on modal sort order.

*Default assumption*: Sort by album count descending in the modal, matching the prominence logic of the top-3.

**7. Modal confirmation model: apply-on-close vs explicit "Done" button.**
The spec does not specify whether genre selections in the modal apply immediately on each tap or only when the modal is closed/confirmed. The existing `Dialog` component has only a close trigger (X button). An immediate-apply model is simpler (no "Done" button needed) and matches the behavior of the top-3 direct toggles.

*Default assumption*: Selections apply immediately as chips are toggled. Closing the modal is not a "confirm" action -- it just dismisses the picker.

**8. Accessibility: the existing `ChipFilter` buttons have no `aria-pressed` attribute.**
The current `<button>` elements toggle visual state via CSS class swapping but do not communicate selection state to screen readers. This pre-dates this spec but should be fixed as part of this work since the component is being reworked.

*Default assumption*: Add `aria-pressed={isSelected(option)}` to chip buttons.

**9. "More" button chip styling.**
Should "More" look like a genre chip or be visually distinct (different color, icon, outlined style)? The spec does not specify.

*Default assumption*: Outlined/ghost variant to distinguish it from selectable genre chips.

---

## Questions (Priority Order)

| # | Question | Stakes | Default |
|---|----------|--------|---------|
| 1 | Should the backend return genre counts, and should `AlbumFilterGetResponse` change to include them? | **Blocks R1 entirely** -- cannot determine top 3 without counts | Yes, modify the schema |
| 2 | In active selection state, how does the user open the modal to modify their selection? | Users get stuck with no way to add genres | Show "More" button alongside selected chips and "Clear" |
| 3 | What happens when selected chips exceed one row on mobile? | Violates the one-row success criterion | Show N chips + "+X" overflow indicator |
| 4 | Should genre filtering use OR logic instead of AND when multiple genres are selected? | AND logic with specific genres (e.g., "Acid Jazz" + "Deep House") will return 0 results, frustrating guests | Keep AND but validate with real collection data |
| 5 | Do top-3 chips act as direct toggles, or do they open the modal? | Affects the "2 taps max" criterion and overall interaction model | Direct toggles |
| 6 | Should modal selections apply immediately or require a "Done" confirmation? | Affects whether users see grid updating behind the modal or only after close | Apply immediately |
| 7 | Should `aria-pressed` be added to chip buttons as part of this work? | Accessibility gap in existing component being reworked | Yes |

---

## Recommended Next Steps

1. **Answer Question 1 first** -- it determines whether this is a frontend-only change or requires a backend API modification + OpenAPI regeneration. The `album_repository.py` `get_filters()` method needs a `COUNT` query grouped by genre value.

2. **Answer Question 2** -- the active-state layout (selected chips + More + Clear) needs to be defined before any component work begins, since it determines the `CollectionSearch` and `ChipFilter` component API changes.

3. **Prototype the one-row constraint** (Question 3) on a 320px viewport with realistic genre names before committing to a layout strategy. The current `flexWrap` approach will not work; this needs either `overflow-x: auto` or a chip-count limiter.

4. **Validate AND vs OR** (Question 4) by querying the actual collection: run a few multi-genre AND queries against the SQLite DB to see how many results they return. If typical multi-genre AND queries return <5 albums, switch to OR.

5. The existing `Dialog` component can be reused for the genre modal with no modification. The `ChipFilter` component needs significant rework: it currently renders all options inline and has no concept of "top N" or "More." Consider splitting into `GenreFilterBar` (top-3 + More + Clear) and reusing `ChipFilter` inside the modal.
