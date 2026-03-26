import { css } from '@styled-system/css';

/** Icon container above the message text */
export const iconStyles = css({
  color: 'onSurface.variant',
  fontSize: '3rem',
  marginBottom: '4',
});

/** Primary message text */
export const messageStyles = css({
  color: 'onSurface',
  fontFamily: 'heading',
  fontSize: 'bodyLg',
  fontWeight: 600,
  textAlign: 'center',
});

/** Root container — centered vertically and horizontally */
export const rootStyles = css({
  alignItems: 'center',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  padding: '12',
});

/** Secondary description text */
export const submessageStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'labelMd',
  marginTop: '2',
  textAlign: 'center',
});
