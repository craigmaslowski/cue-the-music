import { css } from '@styled-system/css';

/** Root container for the queue view */
export const rootStyles = css({
  display: 'flex',
  flexDirection: 'column',
  gap: '2',
  minHeight: '100%',
  paddingBottom: '4',
});

/** Section header for "Up Next" */
export const sectionHeaderStyles = css({
  alignItems: 'baseline',
  display: 'flex',
  gap: '2',
  paddingInline: '4',
  paddingTop: '4',
});

/** "UP NEXT" heading text */
export const sectionTitleStyles = css({
  color: 'onSurface',
  fontFamily: 'heading',
  fontSize: 'headlineLg',
  fontWeight: 700,
  letterSpacing: 'tight',
});

/** Queue count badge */
export const countBadgeStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'labelMd',
  fontWeight: 600,
  textTransform: 'uppercase',
});

/** Container for the up-next list with horizontal padding */
export const listContainerStyles = css({
  paddingInline: '4',
});
