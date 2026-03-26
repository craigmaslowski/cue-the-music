import { css } from '@styled-system/css';

/** 2-column responsive grid for album cards */
export const gridStyles = css({
  display: 'grid',
  gap: '6',
  gridTemplateColumns: 'repeat(2, 1fr)',
  padding: '3',
});

export const gridHeadingStyles = css({
  alignItems: 'center',
  display: 'flex',
  fontSize: 'headlineMd',
  fontWeight: '600',
  gap: '4',
  letterSpacing: 'tight',
  paddingLeft: '4',
});

export const gridHeadingAccentStyles = css({
  '--tw-bg-opacity': 1,
  backgroundColor: 'rgb(243 255 202 / var(--tw-bg-opacity, 1))',
  borderRadius: '0.75rem',
  width: '0.5rem',
  height: '2rem',
});
