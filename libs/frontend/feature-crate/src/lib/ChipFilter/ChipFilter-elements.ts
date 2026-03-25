import { css } from '@styled-system/css';

/** Root container for the chip filter group */
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

/** Scrollable row of chips */
export const chipRowStyles = css({
  display: 'flex',
  flexWrap: 'wrap',
  gap: '2',
});

/** Individual chip — unselected state */
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
});

/** Individual chip — selected state */
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
});
