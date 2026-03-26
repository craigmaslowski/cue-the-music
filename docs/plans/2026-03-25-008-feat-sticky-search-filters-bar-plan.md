---
title: "feat: Sticky search and filter bar on crate view"
type: feat
status: completed
date: 2026-03-25
---

# feat: Sticky search and filter bar on crate view

Make the search input and genre/decade filter chips stick to the top of the scroll area so users can adjust filters without scrolling back up.

## Acceptance Criteria

- [ ] CollectionSearch stays pinned at the top while the album grid scrolls beneath it
- [ ] The sticky bar has a solid/blurred background so album art doesn't show through text
- [ ] No visual jump or layout shift when the bar becomes sticky
- [ ] Works on mobile viewports (the primary use case — phones on a Wi-Fi party network)
- [ ] Album detail overlay still renders above everything

## Context

**Layout hierarchy:**

```
AppShell (rootStyles: height 100dvh, overflow hidden)
  └─ header (position sticky, z-index 10)
  └─ Tabs.Root (tabRootStyles: flex 1, overflow hidden)
      └─ contentStyles (flex 1, overflow auto)  ← THE SCROLL CONTAINER
      │   └─ CrateView (rootStyles: flex column)
      │       └─ CollectionSearch  ← MAKE THIS STICKY
      │       └─ AlbumGrid
      └─ Tabs.List (bottom nav)
```

The scroll container is `contentStyles` (`overflow: auto`). Making `CollectionSearch` sticky within it requires `position: sticky; top: 0` on the CollectionSearch root element, plus a background color and z-index.

## Proposed Solution

**Modify:** `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch-elements.ts`

Add to `rootStyles`:

```typescript
export const rootStyles = css({
  backgroundColor: 'surface',       // solid bg so content scrolls under cleanly
  display: 'flex',
  flexDirection: 'column',
  gap: '3',
  paddingBlock: '3',               // vertical breathing room
  position: 'sticky',
  top: 0,
  zIndex: 5,                       // above album grid, below overlays
});
```

Optionally match the app header's glass blur effect for consistency:

```typescript
backdropFilter: 'blur(token(blurs.glass))',
backgroundColor: 'rgba(14, 14, 14, 0.9)',
```

**No other files need changes.** The CrateView root is a flex column inside the scroll container — `position: sticky` on the first child works natively.

## Sources

- `apps/frontend/src/app/AppShell/AppShell-elements.ts` — scroll container (`contentStyles`) and header glass blur pattern
- `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch-elements.ts` — target file
- `libs/frontend/feature-crate/src/lib/CrateView/CrateView.tsx` — component tree
