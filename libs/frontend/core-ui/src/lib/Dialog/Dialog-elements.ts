import { css } from '@styled-system/css';

/** Semi-transparent backdrop behind the dialog */
export const backdropStyles = css({
  backdropFilter: 'blur(token(blurs.glass))',
  backgroundColor: 'rgba(0, 0, 0, 0.7)',
  inset: 0,
  position: 'fixed',
  zIndex: 50,
});

/** Close trigger button — floating pill in top-right corner */
export const closeTriggerStyles = css({
  alignItems: 'center',
  backdropFilter: 'blur(token(blurs.glass))',
  backgroundColor: 'rgba(40, 40, 40, 0.85)',
  borderRadius: 'full',
  color: 'onSurface',
  cursor: 'pointer',
  display: 'flex',
  fontSize: 'labelMd',
  fontWeight: 600,
  height: '2rem',
  justifyContent: 'center',
  position: 'absolute',
  right: '4',
  top: '4',
  transition: 'background-color 0.15s ease',
  width: '2rem',
  zIndex: 2,
});

/** Main dialog panel — flex column, does not scroll */
export const contentStyles = css({
  backgroundColor: 'surface.containerLowest',
  borderRadius: 'xl',
  boxShadow: 'ambient',
  display: 'flex',
  flexDirection: 'column',
  left: '50%',
  maxHeight: '85vh',
  maxWidth: '500px',
  overflow: 'hidden',
  paddingTop: '6',
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
  paddingInline: '6',
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

/** Scrollable body area between header and close button */
export const scrollBodyStyles = css({
  flex: 1,
  overflowY: 'auto',
  paddingBottom: '6',
  paddingInline: '6',
});

/** Dialog title heading */
export const titleStyles = css({
  color: 'onSurface',
  fontFamily: 'heading',
  fontSize: 'headlineLg',
  fontWeight: 700,
  letterSpacing: 'tight',
  paddingInline: '6',
});
