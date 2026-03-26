import { css } from '@styled-system/css';

/** Root container for vote controls */
export const rootStyles = css({
  alignItems: 'center',
  display: 'flex',
  gap: '3',
});

/** Individual vote button (up or down) */
export const voteButtonStyles = css({
  alignItems: 'center',
  backgroundColor: 'transparent',
  borderWidth: '0',
  cursor: 'pointer',
  display: 'flex',
  gap: '1',
  padding: '1',
  transition: 'opacity 0.15s ease',
  _active: {
    opacity: 0.7,
  },
});

/** Vote count text — muted by default */
export const countStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'labelMd',
  fontWeight: 600,
  minWidth: '1rem',
  textAlign: 'center',
});

/** Up-vote icon — active state uses primary (Electric Lime) */
export const upIconStyles = css({
  color: 'onSurface.variant',
  fontSize: '1.25rem',
  transition: 'color 0.15s ease',
});

/** Up-vote icon active state */
export const upIconActiveStyles = css({
  color: 'primary.container',
  fontSize: '1.25rem',
  transition: 'color 0.15s ease',
});

/** Down-vote icon — active state uses secondary (Hot Pink) */
export const downIconStyles = css({
  color: 'onSurface.variant',
  fontSize: '1.25rem',
  transition: 'color 0.15s ease',
});

/** Down-vote icon active state */
export const downIconActiveStyles = css({
  color: 'secondary',
  fontSize: '1.25rem',
  transition: 'color 0.15s ease',
});

/** Vote count when the corresponding vote is active — up */
export const upCountActiveStyles = css({
  color: 'primary.container',
  fontFamily: 'body',
  fontSize: 'labelMd',
  fontWeight: 600,
  minWidth: '1rem',
  textAlign: 'center',
});

/** Vote count when the corresponding vote is active — down */
export const downCountActiveStyles = css({
  color: 'secondary',
  fontFamily: 'body',
  fontSize: 'labelMd',
  fontWeight: 600,
  minWidth: '1rem',
  textAlign: 'center',
});
