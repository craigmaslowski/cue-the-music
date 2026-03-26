---
title: "feat: Sort genres alphabetically in modal with album counts"
type: feat
status: active
date: 2026-03-25
---

# feat: Sort genres alphabetically in modal with album counts

In the genre filter modal, sort genres by name (A-Z) and show album count in parentheses: `Punk (21)`.

## Proposed Solution

**Modify:** `libs/frontend/feature-crate/src/lib/GenreFilter/GenreFilterModal.tsx`

1. Sort `genres` array by `genre` name (alphabetical) before rendering — use `[...genres].sort((a, b) => a.genre.localeCompare(b.genre))`
2. Change button label from `{g.genre}` to `` {g.genre} ({g.count}) ``

## Acceptance Criteria

- [ ] Genres in modal sorted A-Z by name
- [ ] Each genre shows count in parentheses: `Punk (21)`
- [ ] Top chips on the crate bar remain sorted by count (unchanged)
