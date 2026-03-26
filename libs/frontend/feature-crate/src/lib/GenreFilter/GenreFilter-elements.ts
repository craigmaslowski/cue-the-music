import { css } from '@styled-system/css';

/** Root container for the genre filter bar */
export const rootStyles = css({
  display: 'flex',
  flexDirection: 'column',
  gap: '2',
});

/** Label for the filter group */
export const labelStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'labelMd',
  textTransform: 'uppercase',
});

/** Horizontally scrollable row of chips */
export const chipRowStyles = css({
  display: 'flex',
  gap: '2',
  overflowX: 'auto',
  scrollbarWidth: 'none',
  '&::-webkit-scrollbar': {
    display: 'none',
  },
});

/** Genre chip — unselected state */
export const chipStyles = css({
  backgroundColor: 'surface.variant',
  borderRadius: 'full',
  color: 'onSurface',
  cursor: 'pointer',
  fontFamily: 'body',
  fontSize: 'labelMd',
  paddingBlock: '1.5',
  paddingInline: '3',
  transition: 'background-color 0.15s ease, color 0.15s ease',
  whiteSpace: 'nowrap',
});

/** Genre chip — selected state */
export const chipSelectedStyles = css({
  backgroundColor: 'secondary.container',
  borderRadius: 'full',
  color: 'secondary.onContainer',
  cursor: 'pointer',
  fontFamily: 'body',
  fontSize: 'labelMd',
  paddingBlock: '1.5',
  paddingInline: '3',
  transition: 'background-color 0.15s ease, color 0.15s ease',
  whiteSpace: 'nowrap',
});

/** "More" button — ghost/outlined to distinguish from genre chips */
export const moreButtonStyles = css({
  backgroundColor: 'transparent',
  border: '1px solid token(colors.onSurface.variant)',
  borderRadius: 'full',
  color: 'onSurface.variant',
  cursor: 'pointer',
  fontFamily: 'body',
  fontSize: 'labelMd',
  paddingBlock: '1.5',
  paddingInline: '3',
  transition: 'background-color 0.15s ease, color 0.15s ease',
  whiteSpace: 'nowrap',
});

/** "Clear" button — subtle action button */
export const clearButtonStyles = css({
  backgroundColor: 'transparent',
  border: '1px solid token(colors.onSurface.variant)',
  borderRadius: 'full',
  color: 'onSurface.variant',
  cursor: 'pointer',
  fontFamily: 'body',
  fontSize: 'labelMd',
  paddingBlock: '1.5',
  paddingInline: '3',
  transition: 'background-color 0.15s ease, color 0.15s ease',
  whiteSpace: 'nowrap',
});
