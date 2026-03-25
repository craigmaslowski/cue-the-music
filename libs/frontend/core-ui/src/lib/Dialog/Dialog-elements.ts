import { css } from '@styled-system/css';

/** Semi-transparent backdrop behind the dialog */
export const backdropStyles = css({
  backdropFilter: 'blur(token(blurs.glass))',
  backgroundColor: 'rgba(0, 0, 0, 0.7)',
  inset: 0,
  position: 'fixed',
  zIndex: 50,
});

/** Close trigger button in the top-right corner */
export const closeTriggerStyles = css({
  color: 'onSurface.variant',
  cursor: 'pointer',
  fontSize: 'bodyLg',
  position: 'absolute',
  right: '4',
  top: '4',
});

/** Main dialog panel */
export const contentStyles = css({
  backgroundColor: 'surface.containerHigh',
  borderRadius: 'xl',
  boxShadow: 'ambient',
  left: '50%',
  maxHeight: '85vh',
  maxWidth: '500px',
  overflowY: 'auto',
  padding: '6',
  position: 'fixed',
  top: '50%',
  transform: 'translate(-50%, -50%)',
  width: '90vw',
  zIndex: 51,
});

/** Dialog description text */
export const descriptionStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'bodyLg',
  marginTop: '2',
});

/** Centering container for the dialog */
export const positionerStyles = css({
  alignItems: 'center',
  display: 'flex',
  inset: 0,
  justifyContent: 'center',
  position: 'fixed',
  zIndex: 51,
});

/** Dialog title heading */
export const titleStyles = css({
  color: 'onSurface',
  fontFamily: 'heading',
  fontSize: 'headlineLg',
  fontWeight: 700,
  letterSpacing: 'tight',
});
