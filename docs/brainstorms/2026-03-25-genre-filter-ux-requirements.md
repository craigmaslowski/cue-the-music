---
date: 2026-03-25
topic: genre-filter-ux
---

# Genre Filter UX Improvement

## Problem Frame

The crate page genre filter renders ~100 genre chips in a flex-wrap layout, pushing the album grid far below the fold. Guests browsing the collection must scroll past a wall of genre buttons before seeing any albums, degrading the core browsing experience.

## Requirements

- R1. **Hybrid chip display** — Show the top 3 genres (by album count in the collection) as visible chips, followed by a "More" button to access the full list.
- R2. **Genre modal** — Tapping "More" opens a modal containing all available genres displayed as the existing chip/pill UI. Users can select/deselect genres within the modal.
- R3. **Active selection state** — When one or more genres are selected, replace the default top-3 + "More" view with only the selected genre chips plus a "Clear" button. The "More" button and top-3 chips are hidden while selections are active.
- R4. **Clear resets to default** — Tapping "Clear" removes all genre selections and restores the default top-3 + "More" view.
- R5. **Decade filter unchanged** — The decade chip filter remains as-is (small, bounded set).

## Success Criteria

- The genre filter area never exceeds one row of chips in either state (default or active selection)
- The album grid is visible without scrolling on a typical mobile viewport
- Genre selection/deselection is intuitive with no more than 2 taps to apply a filter

## Scope Boundaries

- No changes to the backend genre API or filtering logic
- No changes to the decade filter
- No genre search/typeahead within the modal (defer unless trivial)
- No persistence of genre selections across sessions

## Key Decisions

- **Top 3 by album count**: Dynamically determined — adapts as the collection changes
- **Modal over popover/dropdown**: ~100 genres warrants a full modal, and we reuse the existing chip style for consistency
- **Replace, don't augment**: Active selections replace the default view entirely rather than appending to it, keeping the filter area compact

## Outstanding Questions

### Deferred to Planning

- [Affects R1][Technical] How should the backend return genre counts, or should the frontend compute top-3 from album data already fetched?
- [Affects R2][Technical] Which modal component to use — ark-ui Dialog or a custom solution?
- [Affects R2][Needs research] Should the modal include a search input for finding genres in the ~100 item list? Low cost to add but may not be needed.

## Next Steps

-> `/ce:plan` for structured implementation planning
