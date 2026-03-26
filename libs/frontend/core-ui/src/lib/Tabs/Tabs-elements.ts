import { css } from '@styled-system/css';

/** Tab content panel area */
export const contentStyles = css({
  flex: 1,
  overflowY: 'auto',
});

/** Horizontal tab trigger list — used as bottom navigation bar */
export const listStyles = css({
  backdropFilter: 'blur(token(blurs.glass))',
  backgroundColor: 'rgba(26, 26, 26, 0.9)',
  display: 'flex',
  gap: '0',
  justifyContent: 'space-around',
  paddingBottom: 'env(safe-area-inset-bottom)',
  width: '100%',
});

/** Root container — fills viewport height with content above, tabs below */
export const rootStyles = css({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  width: '100%',
});

/** Individual tab trigger button */
export const triggerStyles = css({
  backgroundColor: 'transparent',
  borderWidth: '0',
  color: 'onSurface.variant',
  cursor: 'pointer',
  fontFamily: 'heading',
  fontSize: 'body2Xl',
  fontWeight: 600,
  letterSpacing: 'tight',
  padding: '3',
  textTransform: 'uppercase',
  transition: 'color 0.2s ease',
  width: '50%',
  _selected: {
    backgroundColor: 'surface.containerHighest',
    color: 'primary',
  },
});
