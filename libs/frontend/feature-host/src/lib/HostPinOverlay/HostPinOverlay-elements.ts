import { css } from '@styled-system/css';

/** Full-screen dark overlay */
export const overlayStyles = css({
  alignItems: 'center',
  backgroundColor: 'rgba(0, 0, 0, 0.92)',
  display: 'flex',
  flexDirection: 'column',
  height: '100dvh',
  justifyContent: 'center',
  left: 0,
  position: 'fixed',
  top: 0,
  width: '100%',
  zIndex: 50,
});

/** Lock icon at top of overlay */
export const lockIconStyles = css({
  alignItems: 'center',
  backgroundColor: 'secondary.container',
  borderRadius: 'lg',
  display: 'flex',
  height: '48px',
  justifyContent: 'center',
  marginBottom: '4',
  width: '48px',
});

/** "Host Access" title */
export const titleStyles = css({
  color: 'onSurface',
  fontFamily: 'heading',
  fontSize: 'headlineLg',
  fontWeight: 700,
  letterSpacing: 'tight',
  marginBottom: '2',
});

/** Subtitle text */
export const subtitleStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'bodyLg',
  marginBottom: '6',
});

/** Container for the 4 PIN dots */
export const dotContainerStyles = css({
  display: 'flex',
  gap: '3',
  justifyContent: 'center',
  marginBottom: '8',
});

/** Individual PIN dot — unfilled */
export const dotStyles = css({
  backgroundColor: 'surface.variant',
  borderRadius: 'full',
  height: '14px',
  transition: 'background-color 0.15s ease',
  width: '14px',
});

/** PIN dot — filled */
export const dotFilledStyles = css({
  backgroundColor: 'primary.container',
});

/** PIN dot — error state */
export const dotErrorStyles = css({
  backgroundColor: 'secondary',
});

/** Shake animation applied to dot container on error */
export const shakeStyles = css({
  animationDuration: '0.4s',
  animationTimingFunction: 'ease-in-out',
  animationName: 'shake',
});

/** Numeric keypad grid */
export const keypadStyles = css({
  display: 'grid',
  gap: '3',
  gridTemplateColumns: 'repeat(3, 1fr)',
  maxWidth: '280px',
  padding: '0 4',
  width: '100%',
});

/** Individual keypad button */
export const keyStyles = css({
  alignItems: 'center',
  backgroundColor: 'surface.containerHigh',
  borderRadius: 'xl',
  borderWidth: '0',
  color: 'onSurface',
  cursor: 'pointer',
  display: 'flex',
  fontFamily: 'heading',
  fontSize: 'headlineLg',
  fontWeight: 600,
  height: '64px',
  justifyContent: 'center',
  transition: 'background-color 0.15s ease',
  width: '100%',
  _active: {
    backgroundColor: 'surface.bright',
  },
});

/** Action key (clear/backspace) — different color */
export const actionKeyStyles = css({
  alignItems: 'center',
  backgroundColor: 'transparent',
  borderRadius: 'xl',
  borderWidth: '0',
  color: 'onSurface.variant',
  cursor: 'pointer',
  display: 'flex',
  fontSize: 'bodyLg',
  fontWeight: 600,
  height: '64px',
  justifyContent: 'center',
  width: '100%',
  _active: {
    backgroundColor: 'surface.containerHigh',
  },
});

/** Clear action key — red/pink accent */
export const clearKeyStyles = css({
  color: 'secondary',
});
