import { css } from '@styled-system/css';

/** Root container for the host mode indicator bar */
export const rootStyles = css({
  alignItems: 'center',
  display: 'flex',
  gap: '3',
  justifyContent: 'space-between',
  padding: '4',
});

/** Left section with status dot and label */
export const statusStyles = css({
  alignItems: 'center',
  display: 'flex',
  gap: '2',
});

/** Green dot indicator */
export const dotStyles = css({
  backgroundColor: '#22c55e',
  borderRadius: 'full',
  boxShadow: '0 0 8px rgba(34, 197, 94, 0.5)',
  height: '8px',
  width: '8px',
});

/** "HOST MODE ACTIVE" label */
export const labelStyles = css({
  color: '#22c55e',
  fontFamily: 'heading',
  fontSize: 'labelMd',
  fontWeight: 700,
  letterSpacing: 'wider',
  textTransform: 'uppercase',
});

/** Right-side actions container */
export const actionsStyles = css({
  alignItems: 'center',
  display: 'flex',
  gap: '2',
});

/** Deactivate button */
export const deactivateButtonStyles = css({
  backgroundColor: 'transparent',
  borderWidth: '0',
  color: 'onSurface.variant',
  cursor: 'pointer',
  fontFamily: 'body',
  fontSize: 'labelMd',
  padding: '2 3',
  textDecoration: 'underline',
  textDecorationColor: 'onSurface.variant',
  textUnderlineOffset: '2px',
  _disabled: {
    cursor: 'not-allowed',
    opacity: 0.5,
  },
});
