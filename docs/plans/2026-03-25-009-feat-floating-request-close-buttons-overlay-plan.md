---
title: "feat: Floating request and close buttons in album detail overlay"
type: feat
status: completed
date: 2026-03-25
---

# feat: Floating request and close buttons in album detail overlay

## Problem

The album detail overlay scrolls its entire content (cover art, metadata, tracklist, request button). On longer tracklists, the request button disappears below the fold, and the close button (a small "✕") scrolls away and is barely visible. Users must scroll to the bottom to request an album and scroll back up to close the overlay.

## Proposed Solution

Restructure the Dialog content layout so the close button and request button float above scrollable content.

### Layout Change

**Current:**
```
<Content (overflowY: auto, padding: 6)>        ← EVERYTHING scrolls
  <Title>
  {children including request button}
  <CloseTrigger (position: absolute)>           ← scrolls away
</Content>
```

**Proposed:**
```
<Content (overflow: hidden, flex column)>        ← does NOT scroll
  <Title>
  <ScrollBody (flex: 1, overflowY: auto, px: 6)> ← only this scrolls
    {children}
  </ScrollBody>
  <CloseTrigger (position: absolute, z-index)>   ← floats in top-right
</Content>
```

The request button uses `position: sticky; bottom: 0` inside the scroll body so it pins to the bottom of the visible area while content scrolls behind it.

### Files to Modify

#### `libs/frontend/core-ui/src/lib/Dialog/Dialog-elements.ts`

1. **`contentStyles`**: Change `overflowY: 'auto'` to `overflow: 'hidden'`, add `display: 'flex'`, `flexDirection: 'column'`. Move horizontal padding to scroll body.
2. **New `scrollBodyStyles`**: `flex: 1`, `overflowY: 'auto'`, `paddingInline: '6'`, `paddingBottom: '6'`
3. **`closeTriggerStyles`**: Restyle to be prominent — pill shape with semi-transparent background matching the app's dark glass aesthetic. Add `zIndex: 2` to float above scroll content.

#### `libs/frontend/core-ui/src/lib/Dialog/Dialog.tsx`

Wrap `{children}` in `<div className={scrollBodyStyles}>`.

#### `libs/frontend/feature-crate/src/lib/AlbumDetailOverlay/AlbumDetailOverlay-elements.ts`

**`requestButtonStyles`**: Add `position: 'sticky'`, `bottom: 0`, `zIndex: 1`. Add a top gradient mask/shadow so content fades into the button area rather than clipping harshly. Remove `marginTop`.

## Acceptance Criteria

- [ ] Request button stays visible at bottom of overlay regardless of scroll position
- [ ] Close button stays visible in top-right corner regardless of scroll position
- [ ] Close button is visually prominent (pill/rounded shape with background, not just bare "✕")
- [ ] Album content (cover art, metadata, tracklist) scrolls independently between the two buttons
- [ ] Skeleton loading state still renders correctly
- [ ] No z-index conflicts with the backdrop or other overlays

## Sources

- `libs/frontend/core-ui/src/lib/Dialog/Dialog.tsx` — Dialog wrapper (line 32: CloseTrigger)
- `libs/frontend/core-ui/src/lib/Dialog/Dialog-elements.ts` — Dialog styles (line 23: contentStyles, line 13: closeTriggerStyles)
- `libs/frontend/feature-crate/src/lib/AlbumDetailOverlay/AlbumDetailContent.tsx` — request button (line 91-101)
- `libs/frontend/feature-crate/src/lib/AlbumDetailOverlay/AlbumDetailOverlay-elements.ts` — request button styles (line 120)
